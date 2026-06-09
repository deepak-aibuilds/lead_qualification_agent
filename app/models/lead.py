from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db import Base


class Lead(Base):
    __tablename__ = "leads"
    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(255), nullable=False)
    email          = Column(String(255), nullable=False)
    company_name   = Column(String(255), nullable=True)
    company_size   = Column(String(100), nullable=True)   
    budget         = Column(String(100), nullable=True)   
    problem        = Column(Text, nullable=False)
    score          = Column(Integer, nullable=True)        
    classification = Column(String(20), nullable=True)    
    reasoning      = Column(Text, nullable=True)
    email_subject  = Column(String(255), nullable=True)      
    email_draft    = Column(Text, nullable=True)           
    status         = Column(String(50), default="pending") 
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())