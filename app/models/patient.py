from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    phone: str
    age: int
    gender: str

class AnsweredQuestion(BaseModel):
    question: str
    answer: str

class Visit(BaseModel):
    visit_id: str
    form_date: str
    answers: list[AnsweredQuestion]
    previsit_summary: str | None = None
    soap_summary: str | None = None
    postvisit_summary: str | None = None
