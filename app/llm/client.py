
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from langchain_groq import ChatGroq

from typing import Literal
from pathlib import Path
from langsmith import traceable


from dotenv import load_dotenv
load_dotenv()

class LeadQualification(BaseModel):
    lead_score: int
    qualification: Literal['qualified','nurture','disqualified']
    name: str
    company: str
    email: str
    budget: int
    required_service: str
    recommended_action: Literal['Reject',
                                'Send Automated Follow-up',
                                'Book Discovery Call',
                                'Immediate Founder Outreach']


class DraftEmail(BaseModel):
    subject: str
    body: str
    email_to: str

def load_prompt(name: str) -> str:
    path = Path(__file__).parent /  f"{name}.txt"
    return path.read_text()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

prompt_text = load_prompt('prompts/qualify_v1')

prompt = ChatPromptTemplate.from_template(prompt_text)

email_text = load_prompt('prompts/email_v1')
email_prompt = ChatPromptTemplate.from_template(email_text)


def get_chain():
    return prompt | llm.with_structured_output(LeadQualification)


def get_email_chain():
    return email_prompt | llm.with_structured_output(DraftEmail)