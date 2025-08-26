from fastapi import FastAPI
from app.routers import intake

app = FastAPI()
app.include_router(intake.router)
