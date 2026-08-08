from fastapi import FastAPI
from app.routes.interview import router as interview_router

app = FastAPI(title="AI Interview Agent")

app.include_router(interview_router)


@app.get("/")
def root():
    return {
        "message": "AI Interview Agent Backend is running!"
    }