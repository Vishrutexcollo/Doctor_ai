# Intake form schema (Pydantic models)
from pydantic import BaseModel, EmailStr
from typing import List


class QuestionAnswer(BaseModel):
question: str
answer: str


class IntakeRequest(BaseModel):
name: str
phone: str
age: int
gender: str
email: EmailStr
emergency_contact: str
timestamp: str
previsit_summary: str
questions: List[QuestionAnswer]