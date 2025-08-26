from datetime import datetime
from pymongo import ReturnDocument
from app.db import get_database
from app.models.patient import get_patient_by_name_mobile, insert_patient_record

CLINIC_PREFIX = "CLINIC01"

def generate_patient_id(db, name: str, mobile: str) -> str:
    today_str = datetime.now().strftime("%Y%m%d")
    counter = db.patient_counter.find_one_and_update(
        {"_id": today_str},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    seq = str(counter['seq']).zfill(4)
    return f"{CLINIC_PREFIX}-{today_str}-{seq}"

def create_patient_record(data: dict):
    db = get_database()
    existing = get_patient_by_name_mobile(db, data['name'], data['mobile'])
    
    if existing:
        return {"patient_id": existing['patient_id'], "message": "Patient already exists."}
    
    patient_id = generate_patient_id(db, data['name'], data['mobile'])

    new_patient = {
        "patient_id": patient_id,
        "patient_info": data,
        "visits": []
    }
    
    insert_patient_record(db, new_patient)
    return {"patient_id": patient_id, "message": "Patient created."}
