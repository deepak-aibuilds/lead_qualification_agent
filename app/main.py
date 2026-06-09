from fastapi import FastAPI, Depends, Response, Form, HTTPException
from app.db import get_db
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core import logger
import time
from starlette.requests import Request
from typing import Literal
from pydantic import BaseModel
from app.llm import get_chain, get_email_chain
from app.models import Lead

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )

    await FastAPILimiter.init(redis)

    app.state.redis = redis

    yield

    await redis.close()

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



@app.post('/leads', dependencies=[Depends(RateLimiter(times=50, seconds=60))])
async def ingest_leads(
    name: str = Form(...),
    email: str = Form(...),
    company: str = Form(...),
    budget: str = Form(...),
    required_service: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        qualify_chain = get_chain()
        qualification = await qualify_chain.ainvoke({
            'name': name,
            'company': company,
            'email': email,
            'budget': budget,
            'required_service': required_service
        })
    except Exception as e:
        logger.error("qualification_failed", extra={"error": str(e)})
        raise HTTPException(status_code=502, detail="Lead qualification failed")

    try:
        email_chain = get_email_chain()
        email_result = await email_chain.ainvoke({
            'name': name,
            'company': company,
            'email': email,
            'required_service': required_service,
            'budget': budget,
            'lead_score': qualification.lead_score,
            'qualification': qualification.qualification
        })
    except Exception as e:
        logger.error("email_draft_failed", extra={"error": str(e)})
        raise HTTPException(status_code=502, detail="Email generation failed")

    try:
        new_lead = Lead(
            name=name,
            company_name=company,
            budget=budget,
            problem=required_service,
            score=qualification.lead_score,
            classification=qualification.qualification,
            reasoning=qualification.recommended_action,
            email_draft=email_result.body,
            status="scored"
        )
        db.add(new_lead)
        await db.commit()
        await db.refresh(new_lead)
    except Exception as e:
        await db.rollback()
        logger.error("db_save_failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to save lead")

    return {
        "id": new_lead.id,
        "qualification": qualification.qualification,
        "score": qualification.lead_score,
        "recommended_action": qualification.recommended_action,
        "email": email_result.body
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