# app/main.py
from fastapi import FastAPI
from app.routers import intake

def create_app():
    app = FastAPI(title="Clinic AI API")
    app.include_router(intake.router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
