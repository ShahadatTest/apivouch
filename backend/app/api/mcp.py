from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import APP_VERSION
from app.models.db import ProjectRow, engine
from app.schemas.api import ExhaustiveClaimRequest, MCPRequest, OutcomeRequest
from app.services.exhaustiveness import prove_exhaustive_claim
from app.services.importer import extract_endpoints
from app.services.outcomes import execute_verified_outcome, store_receipt
from app.services.runtime import execute_operation

router = APIRouter()

OUTCOME_TOOL = {
    "name": "apivouch_resolve_verified_outcome",
    "title": "Resolve a verified outcome",
    "description": "Call 2-5 independent public providers, enforce price and latency limits, reject invalid or disagreeing results, select the best eligible provider, and return a tamper-evident receipt.",
    "inputSchema": OutcomeRequest.model_json_schema(),
    "outputSchema": {"type": "object", "required": ["verdict", "attempts", "integrity"], "properties": {"verdict": {"type": "string", "enum": ["VERIFIED", "UNVERIFIED"]}, "result": {}, "selected_provider": {"type": ["string", "null"]}, "attempts": {"type": "array"}, "integrity": {"type": "object"}}},
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
}


def _load_project(pid: str) -> tuple[ProjectRow, dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    db = Session(engine, expire_on_commit=False)
    row = db.get(ProjectRow, pid)
    if not row:
        db.close()
        raise HTTPException(404, "Project not found")
    try:
        repair_bundle = json.loads(row.repairs_json or "{}")
        if not isinstance(repair_bundle, dict):
            repair_bundle = {"changes": repair_bundle if isinstance(repair_bundle, list) else [], "contract": None}
        source_spec = json.loads(row.spec_json or "{}")
        spec = repair_bundle.get("contract") or source_spec
        tools = json.loads(row.tools_json or "[]")
    finally:
        db.close()
    return row, spec, tools, source_spec


def _result(request_id: str | int | None, value: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": value}


def _error(request_id: str | int | None, code: int, message: str, data: Any = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _save_proof(pid: str, outcome: dict[str, Any]) -> None:
    db = Session(engine, expire_on_commit=False)
    row = db.get(ProjectRow, pid)
    if row:
        row.proof_json = json.dumps(outcome)
        db.add(row)
        db.commit()
    db.close()


@router.post("/mcp")
async def capability_mcp(request: MCPRequest):
    """Product-level MCP server for APIVouch's verified-outcome capability."""
    if request.method == "initialize":
        requested_version = request.params.get("protocolVersion")
        supported = {"2024-11-05", "2025-03-26", "2025-06-18"}
        protocol_version = requested_version if requested_version in supported else "2025-06-18"
        return _result(request.id, {"protocolVersion": protocol_version, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "APIVouch Outcome Router", "version": APP_VERSION}, "instructions": "Resolve public API outcomes only when independent evidence satisfies the caller's constraints."})
    if request.method == "notifications/initialized":
        return Response(status_code=202)
    if request.method == "ping":
        return _result(request.id, {})
    if request.method == "tools/list":
        return _result(request.id, {"tools": [OUTCOME_TOOL]})
    if request.method == "tools/call":
        if request.params.get("name") != OUTCOME_TOOL["name"]:
            return _error(request.id, -32602, "Unknown tool", {"name": request.params.get("name")})
        try:
            body = OutcomeRequest.model_validate(request.params.get("arguments") or {})
        except ValidationError as exc:
            return _error(request.id, -32602, "Invalid outcome request", {"detail": str(exc)[:500]})
        try:
            receipt = await execute_verified_outcome(body.model_dump())
        except ValueError as exc:
            return _error(request.id, -32602, "Invalid provider set", {"detail": str(exc)})
        store_receipt(receipt)
        return _result(request.id, {"content": [{"type": "text", "text": json.dumps(receipt, ensure_ascii=False)}], "structuredContent": receipt, "isError": receipt["verdict"] != "VERIFIED"})
    return _error(request.id, -32601, "Method not found", {"method": request.method})


@router.post("/mcp/{pid}")
async def mcp_endpoint(pid: str, request: MCPRequest):
    _row, spec, tools, source_spec = _load_project(pid)
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
        if (tool.get("_meta") or {}).get("kind") == "exhaustiveness_gate":
            try:
                claim = ExhaustiveClaimRequest.model_validate(arguments)
            except ValidationError as exc:
                return _error(request.id, -32602, "Invalid exhaustive claim", {"detail": str(exc)[:500]})
            endpoint = next((item for item in extract_endpoints(source_spec) if item.get("operation_id") == claim.operation_id), None)
            if not endpoint:
                return _error(request.id, -32602, "Unknown proof operation", {"operation_id": claim.operation_id})
            outcome = await prove_exhaustive_claim(endpoint, claim.model_dump())
            _save_proof(pid, outcome)
            return _result(
                request.id,
                {
                    "content": [{"type": "text", "text": json.dumps(outcome, ensure_ascii=False)}],
                    "structuredContent": outcome,
                    "isError": not outcome.get("success", False),
                },
            )
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
