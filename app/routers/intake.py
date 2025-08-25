from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import hashlib
from db import get_mongo_client

router = APIRouter()

# --- Step 1: Define request model ---
class PersonalDetails(BaseModel):
    name: str
    mobile: str
    age: int
    gender: str
    email: str
    emergency_contact: str

# --- Step 2: Helper to generate patient_id ---
def generate_patient_id(name: str, phone: str) -> str:
    base = name.strip().lower() + "|" + phone.strip()
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

# --- Step 3: Define route ---
@router.post("/intake")
def intake_form(details: PersonalDetails):
    db = get_mongo_client()
    patients = db["clinicAi"]

    patient_id = generate_patient_id(details.name, details.mobile)
    visit_id = hashlib.sha1(datetime.now().isoformat().encode()).hexdigest()[:10]
    form_date = datetime.utcnow().isoformat()

    visit_entry = {
        "visit_id": visit_id,
        "form_date": form_date,
        "personal_info": details.dict(),
        "intake_qna": [],  # Empty for now
        "previsit_summary": None
    }

    existing = patients.find_one({"patient_id": patient_id})

    if existing:
        patients.update_one(
            {"patient_id": patient_id},
            {"$push": {"visits": visit_entry}}
        )
    else:
        patients.insert_one({
            "patient_id": patient_id,
            "mobile": details.mobile,
            "name": details.name,
            "visits": [visit_entry]
        })

    return {
        "message": "Patient intake saved",
        "patient_id": patient_id,
        "visit_id": visit_id
    }
