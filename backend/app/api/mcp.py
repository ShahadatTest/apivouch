from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import APP_VERSION
from app.models.db import ProjectRow, engine
from app.schemas.api import MCPRequest
from app.services.importer import extract_endpoints
from app.services.runtime import execute_operation

router = APIRouter()


def _load_project(pid: str) -> tuple[ProjectRow, dict[str, Any], list[dict[str, Any]]]:
    db = Session(engine, expire_on_commit=False)
    row = db.get(ProjectRow, pid)
    if not row:
        db.close()
        raise HTTPException(404, "Project not found")
    try:
        repair_bundle = json.loads(row.repairs_json or "{}")
        if not isinstance(repair_bundle, dict):
            repair_bundle = {"changes": repair_bundle if isinstance(repair_bundle, list) else [], "contract": None}
        spec = repair_bundle.get("contract") or json.loads(row.spec_json or "{}")
        tools = json.loads(row.tools_json or "[]")
    finally:
        db.close()
    return row, spec, tools


def _result(request_id: str | int | None, value: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": value}


def _error(request_id: str | int | None, code: int, message: str, data: Any = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


@router.post("/mcp/{pid}")
async def mcp_endpoint(pid: str, request: MCPRequest):
    _row, spec, tools = _load_project(pid)
    if request.method == "initialize":
        requested_version = request.params.get("protocolVersion")
        supported = {"2024-11-05", "2025-03-26", "2025-06-18"}
        protocol_version = requested_version if requested_version in supported else "2025-06-18"
        return _result(
            request.id,
            {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "APIVouch Agent Adapter", "version": APP_VERSION},
                "instructions": "Generated read-only tools call the inspected upstream API through a bounded, schema-validating adapter.",
            },
        )
    if request.method == "notifications/initialized":
        return Response(status_code=202)
    if request.method == "ping":
        return _result(request.id, {})
    if request.method == "tools/list":
        return _result(request.id, {"tools": tools})
    if request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments") or {}
        tool = next((item for item in tools if item.get("name") == tool_name), None)
        if not tool:
            return _error(request.id, -32602, "Unknown tool", {"name": tool_name})
        operation_id = (tool.get("_meta") or {}).get("operation_id")
        endpoint = next((item for item in extract_endpoints(spec) if item.get("operation_id") == operation_id), None)
        if not endpoint:
            return _error(request.id, -32603, "Generated tool has no matching operation")
        outcome = await execute_operation(endpoint, arguments)
        return _result(
            request.id,
            {
                "content": [{"type": "text", "text": json.dumps(outcome, ensure_ascii=False)}],
                "structuredContent": outcome,
                "isError": not outcome.get("success", False),
            },
        )
    return _error(request.id, -32601, "Method not found", {"method": request.method})
