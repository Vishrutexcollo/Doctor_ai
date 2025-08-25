from fastapi import FastAPI
from app.routers import intake, consultation, postvisit

app = FastAPI()

app.include_router(intake.router, prefix="/api")
app.include_router(consultation.router, prefix="/api")
app.include_router(postvisit.router, prefix="/api")
