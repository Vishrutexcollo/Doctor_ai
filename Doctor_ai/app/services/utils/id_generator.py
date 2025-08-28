import hashlib
from datetime import datetime

def generate_patient_id(name: str, phone: str) -> str:
    key = f"{name.strip().lower()}|{phone.strip()}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]

def generate_visit_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")
