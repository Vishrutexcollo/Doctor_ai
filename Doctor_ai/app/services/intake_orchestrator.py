from datetime import datetime
from typing import Optional
from pymongo import ReturnDocument
from app.db import get_database
from app.models.patient import (
    get_patient_by_name_mobile,
    insert_patient_record,
    append_qa_to_visit,
    get_intake_state as _get_intake_state_model,
    mark_intake_complete as _mark_intake_complete_model,
    get_latest_visit_snapshot
)
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

CLINIC_PREFIX = "CLINIC01"
EXAMPLES = [
    "What symptoms are you experiencing today?",
    "How long have you been feeling unwell?",
    "Do you have any ongoing health conditions?"
]

def generate_patient_id(db, name: str, mobile: str) -> str:
    today_str = datetime.now().strftime("%Y%m%d")
    counter = db.patient_counter.find_one_and_update(
        {"_id": today_str},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    seq = str(counter["seq"]).zfill(4)
    return f"{CLINIC_PREFIX}-{today_str}-{seq}"

def create_patient_record(data: dict):
    db = get_database()
    existing = get_patient_by_name_mobile(db, data["name"], data["mobile"])
    if existing:
        return {"patient_id": existing["patient_id"], "message": "Patient already exists."}
    patient_id = generate_patient_id(db, data["name"], data["mobile"])
    insert_patient_record(db, {
        "patient_id": patient_id,
        "patient_info": data,
        "visits": []
    })
    return {"patient_id": patient_id, "message": "Patient record created."}

# ---------- Intake Q&A (already in your code) ----------
def _llm_next_question(prev_qas: list) -> str:
    messages = [
        {"role": "system", "content":
            "You are a clinical assistant AI. Ask one clear, simple question at a time. "
            "Do not repeat topics. Do not switch languages mid-flow. "
            "Aim for ≤10 questions; if information is incomplete, ask up to 2–3 follow-ups. "
            "Examples:\n" + "\n".join(EXAMPLES)
        }
    ]
    for qa in prev_qas:
        messages.append({"role": "user", "content": qa["question"]})
        messages.append({"role": "assistant", "content": qa["answer"]})
    messages.append({"role": "user", "content": "Ask the next best intake question. One sentence only."})

    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=80
    )
    return res.choices[0].message["content"].strip()

def generate_next_question(patient_id: str, latest_answer: Optional[str], start: bool = False):
    db = get_database()
    patient = db.clinicAi.find_one({"patient_id": patient_id}) or {}
    visits = patient.get("visits", [])
    visit = visits[-1] if visits else {}
    prev_qas = visit.get("intake_questionnaire", [])
    question_count = len(prev_qas)

    if question_count == 0 and (start or not latest_answer):
        first_q = EXAMPLES[0]
        return {"question": first_q, "question_number": 1}

    if question_count == 0 and latest_answer:
        default_first_q = EXAMPLES[0]
        append_qa_to_visit(db, patient_id, default_first_q, latest_answer)
        prev_qas = [{"question": default_first_q, "answer": latest_answer}]
        question_count = 1
    elif question_count > 0 and latest_answer:
        last_q = prev_qas[-1]["question"]
        append_qa_to_visit(db, patient_id, last_q, latest_answer)
        # refresh
        patient = db.clinicAi.find_one({"patient_id": patient_id}) or {}
        visits = patient.get("visits", [])
        visit = visits[-1] if visits else {}
        prev_qas = visit.get("intake_questionnaire", [])
        question_count = len(prev_qas)

    if question_count >= 13:
        return {"question": None, "message": "Intake complete."}

    next_q = _llm_next_question(prev_qas)
    return {"question": next_q, "question_number": question_count + 1}

# ---------- NEW: Intake state & complete ----------
def get_intake_state(patient_id: str):
    db = get_database()
    return _get_intake_state_model(db, patient_id)

def _summarize_previsit(prev_qas: list) -> str:
    if not prev_qas:
        return "No intake responses recorded."

    # Try LLM; otherwise fall back to simple bullet list
    try:
        prompt = (
            "Create a brief pre-visit clinical summary from the Q&A below. "
            "Keep it plain and concise (120–180 words). Include: chief complaint, "
            "onset/duration, relevant history, medications/allergies if mentioned, "
            "and any red flags. If a field is unknown, omit it.\n\nQ&A:\n"
            + "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in prev_qas])
        )
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a clinician creating a concise pre-visit summary."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300
        )
        return res.choices[0].message["content"].strip()
    except Exception:
        # Fallback
        lines = [f"- {qa['question']} → {qa['answer']}" for qa in prev_qas]
        return "Pre-visit summary (fallback):\n" + "\n".join(lines)

def complete_intake(patient_id: str, summarize: bool = True):
    db = get_database()
    visit = get_latest_visit_snapshot(db, patient_id)
    qas = visit.get("intake_questionnaire", []) if visit else []
    previsit_summary = _summarize_previsit(qas) if summarize else None
    _mark_intake_complete_model(db, patient_id, previsit_summary)
    state = _get_intake_state_model(db, patient_id)
    return {
        "message": "Intake marked complete.",
        "previsit_summary_added": summarize,
        "state": state
    }
