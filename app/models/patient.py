def get_patient_by_name_mobile(db, name: str, mobile: str):
    return db.clinicAi.find_one({
        "patient_info.name": name,
        "patient_info.mobile": mobile
    })

def insert_patient_record(db, patient_record: dict):
    db.clinicAi.insert_one(patient_record)
