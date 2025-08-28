from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# If you're on Pydantic v2:
from pydantic import ConfigDict

class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str
    mobile: str
    email: Optional[EmailStr] = None
    emergency_contact: Optional[str] = None

class NextQuestionRequest(BaseModel):
    # Accept both "answer" and "latest_answer" keys
    model_config = ConfigDict(populate_by_name=True)
    patient_id: str
    answer: Optional[str] = Field(None, alias="latest_answer")
    start: bool = False

class IntakeCompleteRequest(BaseModel):
    patient_id: str
    summarize: bool = True   # if True, create a previsit_summary from Q&A
