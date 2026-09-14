# APIVouch

**Inspect an API contract, prove its live behavior, generate a safer agent contract, and expose callable MCP tools.**

API documentation can look complete while the live service returns undocumented errors, inconsistent shapes, or values that violate its schema. Those gaps are manageable for a human developer and dangerous for an autonomous agent. APIVouch turns them into structured, reproducible evidence.

> Postman shows whether an endpoint responds. APIVouch shows whether an agent can understand and safely call it.

## What the capability completes

Given a public OpenAPI 3.x or Swagger 2.0 contract, APIVouch:

1. extracts operations and resolves local component references;
2. scores schema quality, documentation, consistency, errors, reliability, and agent usability;
3. performs bounded repeat observations of safe `GET`, `HEAD`, and `OPTIONS` operations;
4. validates JSON, content type, status, and declared response schemas;
5. detects response-shape drift across successful observations;
6. generates an evidence-labelled agent contract and re-analyzes it;
7. exports MCP tool definitions and serves them through a real JSON-RPC MCP endpoint.

Every score is deterministic. The before/after comparison is a re-analysis of two stored contracts—there is no hard-coded score boost and no LLM-generated evidence.

## Five-minute verification

```bash
git clone https://github.com/sklabstudio/apivouch.git
cd apivouch
docker compose up --build
```

Open <http://localhost:8000> and choose **Run self-contained live demo**. The demo imports a deliberately incomplete contract, performs three calls per safe operation, detects two kinds of shape drift, generates an agent contract, and publishes dynamic tools at `/mcp/{project_id}`.

Run the test suite independently:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
```

The current release contains 29 unit and REST/MCP integration tests.

## API surface

| Capability | Endpoint |
|---|---|
| Import a URL or inline contract | `POST /api/projects` |
| Upload JSON/YAML | `POST /api/projects/upload` |
| Static diagnostics | `POST /api/projects/{id}/analyze` |
| Bounded live evidence | `POST /api/projects/{id}/test` |
| Generate evidence-bound contract | `POST /api/projects/{id}/contract` |
| Download generated contract | `GET /api/projects/{id}/contract` |
| Invoke a safe generated operation | `POST /api/projects/{id}/proxy/{operation_id}` |
| Export the complete evidence pack | `GET /api/projects/{id}/export` |
| Dynamic MCP server | `POST /mcp/{id}` |
| Deployment health | `GET /health` |
| X-Agent deployment proof | `GET /.well-known/xagent-verification.json` |

Interactive OpenAPI documentation is available at `/docs`.

## Real MCP flow

Initialize a generated project adapter:

```bash
curl -X POST https://YOUR_DEPLOYMENT/mcp/PROJECT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"initialize",
    "params":{
      "protocolVersion":"2025-06-18",
      "capabilities":{},
      "clientInfo":{"name":"reviewer","version":"1"}
    }
  }'
```

Then call `tools/list` or `tools/call`. A tool result includes a stable envelope:

```json
{
  "success": true,
  "data": {"temperature": 31},
  "error": null,
  "meta": {
    "operation_id": "get_weather",
    "upstream_status": 200,
    "contract_validated": true
  }
}
```

## Safety and capability boundary

- Automatic testing and public tool execution are limited to read-only HTTP methods.
- State-changing operations are documented but return `CONFIRMATION_REQUIRED`; they are never silently converted into `GET` requests.
- URL credentials, localhost, private, link-local, metadata, multicast, reserved, and unspecified IP ranges are blocked in production.
- Every redirect target is revalidated, response bodies are bounded, and request timeouts/retries are capped.
- Imported contracts, observations, and generated artifacts are stored in the configured database. API credentials are not accepted or stored.
- The tool diagnoses contract and runtime compatibility. It is not a vulnerability scanner, security auditor, compliance service, or guarantee that an upstream API is safe.

For local self-testing only, Docker Compose enables `ALLOW_PRIVATE_NETWORK=true`. The deployment blueprint keeps it disabled.

## Evidence model

Generated changes carry a `basis` such as:

- `deterministic` — derived only from contract structure;
- `conservative-default` — a machine-readable placeholder that is explicitly marked generated;
- `N bounded live observation(s)` — inferred only from stored successful JSON payloads;
- `adapter-envelope` — behavior enforced by APIVouch rather than claimed about the upstream.

APIVouch never claims that a generated description or inferred schema came from the API owner.

## Deployment

The repository includes a production root `Dockerfile` and `render.yaml` blueprint. Set:

```text
PROJECT_SLUG=apivouch
GIT_COMMIT=<exact 40-character deployed commit>
DATABASE_URL=sqlite:////tmp/apivouch.db
ALLOW_PRIVATE_NETWORK=false
```

Render supplies `RENDER_GIT_COMMIT`; APIVouch automatically uses it when `GIT_COMMIT` is not set. The health and verification endpoints therefore bind the deployment to the exact reviewed commit.

## Repository map

```text
backend/app/api/          REST, demo, and MCP transports
backend/app/services/     import, analysis, probing, contract, runtime
backend/tests/            unit and API/MCP integration tests
frontend/                 dependency-free responsive workbench
Dockerfile                single-service production image
render.yaml               stable deployment blueprint
```

## Known limits

- External `$ref` documents are not fetched; local JSON pointers are resolved.
- Authenticated endpoints are analyzed but cannot be live-tested by the public service.
- Inferred schemas describe observed samples and are not asserted as the API owner's canonical contract.
- SQLite is suitable for the hackathon review deployment; a long-running multi-instance product should use PostgreSQL and per-user access control.

## Monetization path

The atomic paid capability is an **Agent Readiness Evidence Pack**: one imported contract, bounded live observations, structured findings, an evidence-labelled agent contract, and callable MCP tools. Team plans can add scheduled drift monitoring, private credentials, change alerts, and retained evidence history.

License: MIT. See [LICENSE](LICENSE).
