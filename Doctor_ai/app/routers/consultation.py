from fastapi import APIRouter
router = APIRouter()

@router.post("/consult")
def consult():
    return {"message": "Consultation endpoint"}
from fastapi import APIRouter, Form
from db.connection import patients_collection
from utils.transcriber import transcribe_audio_from_url
from utils.structured_transcript import structure_transcript
from utils.soap_summary import generate_soap_summary

router = APIRouter()

@router.post("/consultation")
def handle_consultation(
    patient_id: str = Form(...),
    visit_id: str = Form(...),
    audio_url: str = Form(...)
):
    # Step 1: Transcribe audio using OpenAI Whisper
    transcript = transcribe_audio_from_url(audio_url)

    # Step 2: Structure the transcript into question-answer pairs
    structured = structure_transcript(transcript)

    # Step 3: Generate SOAP summary
    soap = generate_soap_summary(structured)

    # Step 4: Update patient record in DB
    result = patients_collection.update_one(
        {"patient_id": patient_id, "visits.visit_id": visit_id},
        {"$set": {
            "visits.$.structured_transcript": structured,
            "visits.$.soap_summary": soap,
            "visits.$.raw_transcript": transcript
        }}
    )

    if result.matched_count == 0:
        return {"error": "Patient or visit not found"}

    return {
        "message": "Con
