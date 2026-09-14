from __future__ import annotations

import re
from typing import Any


def to_snake(name: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    value = re.sub(r"[^a-z0-9_-]+", "_", value).strip("_-")
    return (value or "operation")[:64]


def _request_body_schema(request_body: dict[str, Any]) -> dict[str, Any] | None:
    if not request_body:
        return None
    if isinstance(request_body.get("schema"), dict):
        return request_body["schema"]
    content = request_body.get("content") or {}
    if isinstance(content, dict):
        media = content.get("application/json") or next((item for item in content.values() if isinstance(item, dict)), None)
        if isinstance(media, dict) and isinstance(media.get("schema"), dict):
            return media["schema"]
    return None


def input_schema_for_endpoint(endpoint: dict[str, Any]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []
    for parameter in endpoint.get("parameters") or []:
        if not isinstance(parameter, dict):
            continue
        parameter_name = str(parameter.get("name") or "argument")
        schema = dict(parameter.get("schema") or {})
        if not schema and parameter.get("type"):
            schema = {"type": parameter["type"]}
        schema.setdefault("type", "string")
        if parameter.get("description"):
            schema["description"] = parameter["description"]
        schema["x-location"] = parameter.get("in") or "query"
        properties[parameter_name] = schema
        if parameter.get("required"):
            required.append(parameter_name)
    body_schema = _request_body_schema(endpoint.get("requestBody") or {})
    if body_schema:
        properties["body"] = body_schema
        if endpoint["requestBody"].get("required"):
            required.append("body")
    input_schema: dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        input_schema["required"] = sorted(set(required))
    return input_schema


def generate_tools(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for endpoint in endpoints:
        operation_id = endpoint.get("operation_id") or "operation"
        base_name = to_snake(operation_id)
        name = base_name
        suffix = 2
        while name in used_names:
            name = f"{base_name[:60]}_{suffix}"
            suffix += 1
        used_names.add(name)
        input_schema = input_schema_for_endpoint(endpoint)
        response_data_schema = endpoint.get("response_schema") or {}
        output_schema = {
            "type": "object",
            "required": ["success"],
            "properties": {
                "success": {"type": "boolean"},
                "data": response_data_schema,
                "error": {
                    "type": ["object", "null"],
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "retryable": {"type": "boolean"},
                    },
                },
                "meta": {"type": "object"},
            },
        }
        read_only = endpoint["method"] in {"GET", "HEAD", "OPTIONS"}
        description = (endpoint.get("description") or endpoint.get("summary") or f"Call {endpoint['method']} {endpoint['path']}").strip()[:500]
        if not read_only:
            description += " Explicit confirmation is required because this operation may change external state."
        tools.append(
            {
                "name": name,
                "title": endpoint.get("summary") or operation_id,
                "description": description,
                "inputSchema": input_schema,
                "outputSchema": output_schema,
                "annotations": {
                    "readOnlyHint": read_only,
                    "destructiveHint": not read_only,
                    "idempotentHint": endpoint["method"] in {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"},
                    "openWorldHint": True,
                },
                "_meta": {"operation_id": operation_id, "method": endpoint["method"], "path": endpoint["path"]},
            }
        )
    return tools
