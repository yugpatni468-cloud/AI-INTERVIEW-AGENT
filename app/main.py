from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.candidates import router as candidates_router
from app.routes.interview import router as interview_router


app = FastAPI(
    title="AI Interview Agent",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-interview-agent-seven-roan.vercel.app",
        "https://ai-interview-agent-three-orcin.vercel.app",
        "https://ai-interview-agent-69n34gsad-code-xverse.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    candidates_router
)

app.include_router(
    interview_router
)


@app.get("/")
def root():

    return {
        "message": "AI Interview Agent API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }