from datetime import datetime

def get_patient_by_name_mobile(db, name: str, mobile: str):
    return db.clinicAi.find_one({
        "patient_info.name": name,
        "patient_info.mobile": mobile
    })

def insert_patient_record(db, patient_record: dict):
    db.clinicAi.insert_one(patient_record)

def _today_ids():
    today_str = datetime.today().strftime("%Y-%m-%d")
    visit_id = "V" + today_str.replace("-", "")
    return today_str, visit_id

def ensure_today_visit(db, patient_id: str):
    today_str, visit_id = _today_ids()
    # Create visit if it doesn't exist
    if not db.clinicAi.find_one({"patient_id": patient_id, "visits.visit_id": visit_id}):
        db.clinicAi.update_one(
            {"patient_id": patient_id},
            {"$push": {
                "visits": {
                    "visit_id": visit_id,
                    "date": today_str,
                    "intake_questionnaire": [],
                    "intake_complete": False
                }
            }}
        )
    return visit_id

def get_latest_visit_snapshot(db, patient_id: str):
    doc = db.clinicAi.find_one(
        {"patient_id": patient_id},
        {"_id": 0, "visits": {"$slice": -1}, "patient_id": 1}
    )
    if not doc or not doc.get("visits"):
        return None
    return doc["visits"][0]

def append_qa_to_visit(db, patient_id: str, question: str, answer: str):
    # Ensure today's visit exists
    visit_id = ensure_today_visit(db, patient_id)
    db.clinicAi.update_one(
        {"patient_id": patient_id, "visits.visit_id": visit_id},
        {"$push": {
            "visits.$.intake_questionnaire": {
                "question": question,
                "answer": answer
            }
        }}
    )

def mark_intake_complete(db, patient_id: str, previsit_summary: str | None):
    visit = get_latest_visit_snapshot(db, patient_id)
    if not visit:
        # nothing to mark; create today and mark done
        visit_id = ensure_today_visit(db, patient_id)
    else:
        visit_id = visit["visit_id"]

    set_fields = {
        "visits.$.intake_complete": True,
        "visits.$.intake_completed_at": datetime.utcnow().isoformat()
    }
    if previsit_summary is not None:
        set_fields["visits.$.previsit_summary"] = previsit_summary

    db.clinicAi.update_one(
        {"patient_id": patient_id, "visits.visit_id": visit_id},
        {"$set": set_fields}
    )

def get_intake_state(db, patient_id: str):
    visit = get_latest_visit_snapshot(db, patient_id)
    if not visit:
        return {
            "patient_id": patient_id,
            "started": False,
            "intake_complete": False,
            "question_count": 0,
            "intake_questionnaire": []
        }

    qas = visit.get("intake_questionnaire", [])
    return {
        "patient_id": patient_id,
        "visit_id": visit.get("visit_id"),
        "date": visit.get("date"),
        "started": len(qas) > 0,
        "intake_complete": visit.get("intake_complete", False),
        "question_count": len(qas),
        "last_question": qas[-1]["question"] if qas else None,
        "last_answer": qas[-1]["answer"] if qas else None,
        "intake_questionnaire": qas
    }
