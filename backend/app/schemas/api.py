from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    openapi_url: str | None = None
    openapi_json: dict[str, Any] | None = None


class AnalyzeResponse(BaseModel):
    project_id: str
    endpoints: int
    score: dict[str, Any]
    issues: list[dict[str, Any]]


class ProxyRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class TestRequest(BaseModel):
    samples_per_endpoint: int = Field(default=2, ge=1, le=5)
    arguments: dict[str, dict[str, Any]] = Field(default_factory=dict)


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
