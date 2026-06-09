from fastapi import FastAPI, Depends, Response, Form, HTTPException, BackgroundTasks
from app.db import get_db
from contextlib import asynccontextmanager
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.core import logger
import time
from starlette.requests import Request
from pydantic import BaseModel
from app.models import Lead
from app.services import qualify_email_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
class EmailModel(BaseModel):
    name: str
    company: str
    email: str
    required_service: str
    budget: int
    lead_score : int
    qualification: str

@app.middleware('http')
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        'request',
         extra={
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
        }

    )
    return response

@app.post('/leads', dependencies=[
    Depends(RateLimiter(limiter=Limiter(Rate(50, Duration.MINUTE))))
])
async def ing_leads(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    company: str = Form(...),
    budget: str = Form(...),
    required_service: str = Form(...),
    db: AsyncSession = Depends(get_db)
    
):
    try:
        new_lead = Lead(
            name=name,
            company_name=company,
            budget=budget,
            problem=required_service,
            email=email
        )
        db.add(new_lead)
        await db.commit()
        await db.refresh(new_lead)
    except Exception as e:
        await db.rollback()
        logger.error("db_save_failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to save lead")
    background_tasks.add_task(qualify_email_agent, new_lead.id)
    return {
     'id': new_lead.id,
     'status': new_lead.status
    }


@app.get('/leads/{id}')
async def get_lead(id:int, db: AsyncSession = Depends(get_db)):
    lead_db = await db.execute(select(Lead).where(Lead.id == id))
    lead= lead_db.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail='Lead Not Found')
    return {
        "lead_id":lead.id,
        'lead_status': lead.status,
        "lead_score":lead.score,
        "lead_qualification":lead.classification,
        'email_subject':lead.email_subject,
        'email_body':lead.email_draft
    }


   




@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), response: Response = None):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health check failed", extra={"error": str(e)})
        response.status_code = 503
        return {"status": "unhealthy"}