from fastapi import APIRouter
router = APIRouter()

@router.post("/consult")
def consult():
    return {"message": "Consultation endpoint"}
