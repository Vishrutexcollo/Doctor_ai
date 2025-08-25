from fastapi import APIRouter
router = APIRouter()

@router.post("/intake")
def intake_form():
    return {"message": "Intake form endpoint"}
