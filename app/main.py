from fastapi import FastAPI, Depends, Response, Form
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



@app.post('/leads', dependencies=[
    Depends(RateLimiter(times=5,seconds=60))
])
async def ingest_leads(
    name: str = Form(...),
    email: str = Form(...),
    company:str = Form(...),
    budget:str = Form(...),
    required_service: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    chain = get_chain()
    save_response = await chain.ainvoke({
        'name': name,
        'company': company,
        'email': email,
        'budget': budget,
        'required_service': required_service
    })
    chain = get_email_chain()
    email_response = await chain.ainvoke({
                'name':name,
                'company':company,
               'email':email,
                'required_service':required_service,
                'budget':budget,
                'lead_score':save_response.lead_score,
                'qualification':save_response.qualification
    })
    new_lead = Lead(
        name = name,
        company_name = company,
        budget = budget,
        problem = required_service,
        score = save_response.lead_score,
        classification = save_response.qualification,
        email_draft = email_response.body
    )
    db.add(new_lead)
    await db.commit()
    return {"email": email_response.body}


    


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), response: Response = None):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health check failed", extra={"error": str(e)})
        response.status_code = 503
        return {"status": "unhealthy"}