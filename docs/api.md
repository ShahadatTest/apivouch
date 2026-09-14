# API contract

All responses are JSON unless otherwise noted. Interactive documentation is served at `/docs`.

## Project lifecycle

### `POST /api/projects`

Import a public URL or inline object.

```json
{
  "name": "Weather API",
  "openapi_url": "https://api.example.com/openapi.json"
}
```

Use `openapi_json` instead of `openapi_url` for an inline contract. Limits: 200 operations and a 512 KiB import body by default.

### `POST /api/projects/upload`

Multipart fields: `name` and `file`. JSON and YAML are accepted.

### `GET /api/projects/{id}`

Returns source endpoints, current source score, findings, live comparison, and contract state.

### `POST /api/projects/{id}/test`

```json
{
  "samples_per_endpoint": 3,
  "arguments": {
    "getWeather": {"city": "Dhaka", "units": "metric"}
  }
}
```

Only `GET`, `HEAD`, and `OPTIONS` are automatically called. Required arguments that are not supplied produce a structured `skipped` result.

### `POST /api/projects/{id}/contract`

Generates an evidence-bound agent contract. The deprecated `/repair` alias is kept for compatibility; neither route mutates the upstream service. The comparison is produced by re-running the same deterministic evaluator against the source and generated contracts.

### `GET /api/projects/{id}/contract`

Returns the generated OpenAPI/Swagger agent contract. Returns HTTP 409 until generation is complete.

### `GET /api/projects/{id}/comparison`

Returns the stored source-versus-generated-contract comparison.

### `POST /api/projects/{id}/proxy/{operation_id}`

Request:

```json
{"arguments":{"city":"Dhaka"}}
```

Read-only operations return a stable `{success,data,error,meta}` envelope. State-changing operations return `CONFIRMATION_REQUIRED`.

### `GET /api/projects/{id}/export`

Returns the complete `apivouch-agent-pack-v1`: score, observations, findings, changes, generated contract, MCP tools, comparison, and MCP endpoint.

### `DELETE /api/projects/{id}`

Deletes exactly one stored project.

## MCP transport

`POST /mcp/{project_id}` accepts JSON-RPC 2.0 methods:

- `initialize`
- `notifications/initialized`
- `ping`
- `tools/list`
- `tools/call`

Supported protocol versions: `2024-11-05`, `2025-03-26`, and `2025-06-18`.

## Deployment evidence

- `GET /health` returns `status`, service version, and the exact deployed commit.
- `GET /.well-known/xagent-verification.json` returns schema version, submission slug, and the same commit.
