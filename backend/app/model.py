# backend/app/models.py
from typing import List
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[str]
