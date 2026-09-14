# APIVouch

**Route one agent goal across independent APIs, reject bad evidence, and return one verified outcome with a tamper-evident receipt.**

An autonomous agent should not trust the first API that answers. A provider can be unavailable, over budget, too slow, schema-invalid, or simply disagree with every independent source. APIVouch calls multiple public providers concurrently, enforces the caller's constraints, selects only from an agreeing evidence group, and binds the decision to the deployed source commit.

> Agents do not need another API directory. They need proof that the outcome they are about to use survived independent verification.

## The 30-second demo

Open the deployed app and click **Resolve verified outcome**. Four live HTTP providers compete to return the same delivery quote:

- two provider fixtures return agreeing numeric results;
- one returns the wrong type;
- one returns HTTP 503.

APIVouch rejects the bad evidence, selects the best eligible provider under cost and latency limits, stores the receipt, and verifies its SHA-256 integrity after reading it back. The one-click flow is explicitly labelled as a self-contained demo; normal API and MCP requests require distinct provider network origins, including after redirects. The demo is also honest about settlement: price is quoted, but no payment is moved yet.

The same capability is agent-callable through the product-level MCP endpoint at `POST /mcp` with tool `apivouch_resolve_verified_outcome`.

## What the capability completes

Given a public OpenAPI 3.x or Swagger 2.0 contract, APIVouch:

1. extracts operations and resolves local component references;
2. scores schema quality, documentation, consistency, errors, reliability, and agent usability;
3. performs bounded repeat observations of safe `GET`, `HEAD`, and `OPTIONS` operations;
4. validates JSON, content type, status, and declared response schemas;
5. detects response-shape drift across successful observations;
6. generates an evidence-labelled agent contract and re-analyzes it;
7. exports MCP tool definitions and serves them through a real JSON-RPC MCP endpoint.
8. proves exhaustive collection claims by traversing bounded pagination itself—never by trusting agent-supplied counts or cursors.

Across independent providers, APIVouch additionally:

1. accepts a goal, two to five public providers, extraction paths, response schemas, and price/latency constraints;
2. calls affordable providers concurrently through the same bounded SSRF-safe transport;
3. rejects HTTP errors, invalid JSON, missing result paths, schema mismatches, over-budget providers, and outliers;
4. requires configurable independent agreement, including numeric tolerance;
5. deterministically selects the strongest eligible provider and returns `VERIFIED` or refuses with `UNVERIFIED`;
6. stores a commit-bound receipt whose integrity can be recomputed without trusting APIVouch.

Receipts bind the redacted provider URL, a digest of the exact request URL, resolved origin, result path, expected-schema digest, full-response digest, extracted-value digest, observed status/latency, selection policy, and deployment commit. `examples/verify_outcome_receipt.py` verifies the content address offline with only Python's standard library.

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

The current release contains 46 unit and REST/MCP integration tests.

## API surface

| Capability | Endpoint |
|---|---|
| Resolve a constrained, verified outcome | `POST /api/outcomes/execute` |
| Run the four-provider judge demo | `POST /api/outcomes/demo` |
| Retrieve and re-verify a receipt | `GET /api/outcomes/receipts/{id}` |
| Product-level outcome MCP server | `POST /mcp` |
| Import a URL or inline contract | `POST /api/projects` |
| Upload JSON/YAML | `POST /api/projects/upload` |
| Static diagnostics | `POST /api/projects/{id}/analyze` |
| Bounded live evidence | `POST /api/projects/{id}/test` |
| Prove `ALL` / `NONE` / count / min / max | `POST /api/projects/{id}/prove` |
| Generate evidence-bound contract | `POST /api/projects/{id}/contract` |
| Download generated contract | `GET /api/projects/{id}/contract` |
| Invoke a safe generated operation | `POST /api/projects/{id}/proxy/{operation_id}` |
| Export the complete evidence pack | `GET /api/projects/{id}/export` |
| Dynamic MCP server | `POST /mcp/{id}` |
| Deployment health | `GET /health` |
| X-Agent deployment proof | `GET /.well-known/xagent-verification.json` |

Interactive OpenAPI documentation is available at `/docs`.

## Verified-outcome request

```json
{
  "goal": "Get a verified delivery quote",
  "providers": [
    {
      "name": "provider-a",
      "url": "https://provider-a.example/quote",
      "result_path": "quote.amount_usd",
      "expected_schema": {"type": "number", "minimum": 0},
      "price_usd": 0.004
    },
    {
      "name": "provider-b",
      "url": "https://provider-b.example/quote",
      "result_path": "quote.amount_usd",
      "expected_schema": {"type": "number", "minimum": 0},
      "price_usd": 0.003
    }
  ],
  "constraints": {
    "max_price_usd": 0.01,
    "max_latency_ms": 3000,
    "minimum_agreement": 2,
    "numeric_tolerance_percent": 1
  }
}
```

No provider is selected when the agreement requirement is not met. An `UNVERIFIED` response is a successful safety decision, not a fabricated best guess.

Verify an exported receipt independently:

```bash
python examples/verify_outcome_receipt.py receipt.json
```

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

Every project with a `GET` operation also exposes `apivouch_prove_exhaustive_claim`. It rejects client-supplied evidence, starts at the first page, follows cursor/page/offset pagination within deployment caps, and checks page repetition, cursor progress, snapshot stability, and authoritative totals. Its verdict is `PROVEN`, `CONDITIONAL` (complete traversal without a declared snapshot), or `UNPROVEN`; a failed obligation can never receive a certificate. The latest result is stored with the project and included in its exported evidence pack.

## Safety and capability boundary

- Automatic testing and public tool execution are limited to read-only HTTP methods.
- Outcome routing accepts credential-free public `GET` providers only; URL query values are redacted from stored receipts.
- State-changing operations are documented but return `CONFIRMATION_REQUIRED`; they are never silently converted into `GET` requests.
- URL credentials, localhost, private, link-local, metadata, multicast, reserved, and unspecified IP ranges are blocked in production.
- Every redirect target is revalidated, response bodies are bounded, and request timeouts/retries are capped.
- Exhaustiveness proof collection defaults to at most 20 pages and 5,000 records; the server cap always wins over a caller's requested limit.
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
- Pagination is auto-detected for common cursor, page, and offset conventions; unusual APIs can supply response paths and the request token parameter, but cannot supply observed evidence.
- Inferred schemas describe observed samples and are not asserted as the API owner's canonical contract.
- SQLite is suitable for the hackathon review deployment; a long-running multi-instance product should use PostgreSQL and per-user access control.

## Monetization path

The atomic commercial capability is a **Verified Outcome**: concurrent provider evaluation, constraint enforcement, deterministic selection, and an integrity receipt. The current public build quotes provider prices but deliberately does not claim or simulate settlement. A production tier can add x402 payment after verification, retained evidence history, private providers, scheduled drift monitoring, and outcome SLAs.

License: MIT. See [LICENSE](LICENSE).
