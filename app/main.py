from fastapi import FastAPI, Depends, Response, Form
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core import logger
import time
from starlette.requests import Request
from typing import Literal
from pydantic import BaseModel
from app.llm import get_chain, LeadQualification, get_email_chain, DraftEmail
app = FastAPI()


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



@app.post('/leads', response_model=LeadQualification)
async def ingest_leads(
    name: str = Form(...),
    email: str = Form(...),
    company:str = Form(...),
    budget:str = Form(...),
    required_service: str = Form(...)
):
    chain = get_chain()
    response = await chain.ainvoke({
        'name': name,
        'company': company,
        'email': email,
        'budget': budget,
        'required_service': required_service
    })
    return response

@app.post('/email',response_model=DraftEmail)
async def draf_email(
    request: EmailModel
):
    chain = get_email_chain()
    response = await chain.ainvoke({
                'name':request.name,
                'company':request.company,
               'email':request.email,
                'required_service':request.required_service,
                'budget':request.budget,
                'lead_score':request.lead_score ,
                'qualification':request.qualification
    })
    return response

    


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), response: Response = None):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health check failed", extra={"error": str(e)})
        response.status_code = 503
        return {"status": "unhealthy"}