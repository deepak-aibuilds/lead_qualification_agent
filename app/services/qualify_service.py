from app.models import Lead
from app.db import AsyncSessionLocal
from sqlalchemy import select
from app.llm import get_chain, get_email_chain


async def qualify_email_agent(id):
     async with AsyncSessionLocal() as db:
        lead_db = await db.execute(select(Lead).where(Lead.id == id))
        lead = lead_db.scalars().first()
        try:
            qualify_chain = get_chain()
            qualification = await qualify_chain.ainvoke({
                'name': lead.name,
                'company': lead.company_name,
                'email': lead.email,
                'budget': lead.budget,
                'required_service': lead.problem
            })
        
            
            lead.score=qualification.lead_score
            lead.classification=qualification.qualification
            lead.reasoning=qualification.recommended_action
            lead.status = 'scored'
            

            email_chain = get_email_chain()
            email_result = await email_chain.ainvoke({
                'name': lead.name,
                'company': lead.company_name,
                'email': lead.email,
                'required_service': lead.problem,
                'budget': lead.budget,
                'lead_score': lead.score,
                'qualification': lead.classification
            })
            lead.email_draft = email_result.body
            lead.email_subject = email_result.subject
            await db.commit()
            await db.refresh(lead)
            return {
            "id": lead.id,
            "qualification": lead.classification,
            "score": lead.score,
            "recommended_action": qualification.recommended_action,
            "email_subject": email_result.email_subject,
            'email_body': email_result.body
        }
        except Exception as e:
            lead.status = 'failed'
            await db.commit()
            print(f"qualify_email_agent failed for lead {id}: {e}")
      