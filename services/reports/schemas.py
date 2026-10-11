"""Validated request and response shapes."""
from typing import Any, Literal

from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    county: str = "unknown"
    language: Literal["en", "sw", "sheng"] = "en"
    image_tags: list[str] = Field(default_factory=list, max_length=20)
    has_person: bool = False
    photo_ref: str | None = None


class MessageOut(BaseModel):
    status: Literal["ok", "forbidden"]
    route: str
    tool: str | None
    mode: Literal["stub", "live"]
    prompt_version: str
    model_id: str
    result: dict[str, Any]


class ApproveOut(BaseModel):
    alert_id: str
    status: Literal["approved"]
    approved_by: str
