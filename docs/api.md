# API contract

All responses are JSON unless otherwise noted. Interactive documentation is served at `/docs`.

## Verified outcomes

### `POST /api/outcomes/execute`

Calls two to five credential-free public `GET` providers concurrently. Each provider declares a URL, optional dotted `result_path`, optional JSON Schema, and quoted `price_usd`. Constraints set maximum selected-provider price, maximum latency, minimum agreeing providers, and numeric tolerance.

Configured providers must have unique network origins. Redirects are resolved through the bounded fetcher and duplicate final origins are rejected as well. URL query values are used for the request but redacted from the receipt.

The response is an `apivouch-outcome-receipt-v1`. `VERIFIED` includes a selected result and provider. `UNVERIFIED` always has a null result/provider and zero selected price.

### `POST /api/outcomes/demo`

Runs the explicitly self-contained four-fixture demonstration. Its receipt sets `provider_independence.required` to `false`; this bypass is not available in caller-supplied REST or MCP requests.

### `POST /api/outcomes/live-demo`

Calls Frankfurter, Floatrates, and ExchangeRate-API at distinct public origins to resolve a USD→EUR reference rate. It uses the same origin, schema, latency, agreement, selection, storage, and integrity path as caller-supplied requests; no demo bypass is active.

### `GET /api/outcomes/receipts/{receipt_id}`

Returns the stored receipt and `integrity_valid`, recomputed from its canonical JSON without trusting the stored fingerprint.

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

### `POST /api/projects/{id}/prove`

```json
{
  "operation_id": "listItems",
  "claim_type": "EXACT_COUNT",
  "expected_count": 7,
  "arguments": {"limit": 3}
}
```

Supported claims are `ALL`, `NONE`, `EXACT_COUNT`, `MIN`, and `MAX`. For min/max, add `field`, optional `candidate_id`, and optional `id_field`. Common cursor, page, and offset APIs are auto-detected; a `pagination` object can set dotted response paths and bounded limits.

The input deliberately has no evidence fields. APIVouch begins at the first page and records response digests, hashed cursor progress, record/page counts, snapshot consistency, and authoritative-total consistency. Results use `PROVEN`, `CONDITIONAL`, or `UNPROVEN`. Only the first two can include a content-addressed certificate.

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

Returns the complete `apivouch-agent-pack-v1`: score, observations, findings, changes, generated contract, MCP tools, comparison, latest exhaustiveness proof, and MCP endpoint.

### `DELETE /api/projects/{id}`

Deletes exactly one stored project.

## MCP transport

`POST /mcp` is the product-level MCP server. It exposes `apivouch_resolve_verified_outcome` with the same validation, selection, receipt, and refusal semantics as the REST endpoint.

`POST /mcp/{project_id}` accepts JSON-RPC 2.0 methods:

- `initialize`
- `notifications/initialized`
- `ping`
- `tools/list`
- `tools/call`

Supported protocol versions: `2024-11-05`, `2025-03-26`, and `2025-06-18`.

`tools/list` includes `apivouch_prove_exhaustive_claim` whenever the project has a GET operation. It uses the same proof collector as the REST route.

## Deployment evidence

- `GET /health` returns `status`, service version, and the exact deployed commit.
- `GET /.well-known/xagent-verification.json` returns schema version, submission slug, and the same commit.
