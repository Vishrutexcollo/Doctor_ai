from fastapi import APIRouter, Query
from app.schemas.intake_schema import PatientInfo, NextQuestionRequest, IntakeCompleteRequest
from app.services.intake_orchestrator import (
    create_patient_record,
    generate_next_question,
    get_intake_state,
    complete_intake
)

router = APIRouter(prefix="/intake", tags=["Intake"])

@router.post("/patient-info")
def submit_patient_info(info: PatientInfo):
    return create_patient_record(info.dict())

@router.post("/next-question")
def post_next_question(req: NextQuestionRequest):
    return generate_next_question(req.patient_id, req.answer, start=req.start)

@router.get("/state")
def read_intake_state(patient_id: str = Query(..., description="Patient ID to fetch current intake state")):
    return get_intake_state(patient_id)

@router.post("/complete")
def post_intake_complete(req: IntakeCompleteRequest):
    return complete_intake(req.patient_id, summarize=req.summarize)
