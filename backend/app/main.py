from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .model import AskRequest, AskResponse
from .rag import rag_pipeline

app = FastAPI(title="Quorium RAG Challenge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ok for local dev; can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    answer, sources = rag_pipeline.answer_question(request.question)
    return AskResponse(answer=answer, sources=sources)
