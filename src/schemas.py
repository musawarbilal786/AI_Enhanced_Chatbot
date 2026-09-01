from __future__ import annotations
from typing import Any, Literal, TypedDict
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    id: str
    title: str
    category: str
    campus_scope: str = "Ulster University / London branch campus"
    url: str = ""
    text: str
    last_verified: str = ""
    source_type: Literal["pdf", "web", "manual"] = "manual"
    filename: str = ""
    page: int | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    url: str = ""
    category: str
    text: str
    score: float
    source_type: str = "manual"
    filename: str = ""
    page: int | None = None


class IntentResult(BaseModel):
    intent: Literal["regulation_query", "support_query", "greeting", "unsafe_or_personal"]
    normalized_query: str
    topics: list[str] = Field(default_factory=list)
    needs_retrieval: bool = True


class CritiqueResult(BaseModel):
    grounded: bool
    complete: bool
    safe: bool
    needs_revision: bool
    issues: list[str] = Field(default_factory=list)


class AgentState(TypedDict, total=False):
    question: str
    chat_history: list[dict[str, str]]
    intent: dict[str, Any]
    retrieved: list[dict[str, Any]]
    context: str
    draft_answer: str
    critique: dict[str, Any]
    final_answer: str
    citations: list[dict[str, Any]]
    revision_count: int
    error: str
