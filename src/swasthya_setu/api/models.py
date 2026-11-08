"""Pydantic models for the public API."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)
    language: Literal["en", "hi", "or", "pa"] | None = None


class SourceResponse(BaseModel):
    number: int
    source: str
    page: str
    snippet: str
    publisher: str | None = None
    year: int | None = None
    url: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[int] = Field(default_factory=list)
    sources: list[SourceResponse] = Field(default_factory=list)
    intent: str
    language: str
    emergency: bool
    language_consistent: bool
    request_id: str


class FeedbackRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    accepted: bool
    request_id: str
