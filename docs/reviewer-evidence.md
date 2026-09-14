# Reviewer evidence map

This document points to evidence; it does not assign a score or claim acceptance.

## Hard gates

| Gate | Evidence after deployment |
|---|---|
| Callable | Root verified-outcome demo, `/docs`, product MCP at `/mcp`, project REST API, and `/mcp/{project_id}` |
| Version-bound | `/health` and `/.well-known/xagent-verification.json` return the deployed 40-character commit |
| Reproducible | Pinned dependencies, root Dockerfile, Docker Compose, Render blueprint, exact test/run commands |
| Safe to evaluate | Read-only automatic boundary, structured errors, bounded network calls, SSRF checks, no accepted/stored credentials |
| Useful for agents | Multi-provider outcome routing, JSON Schemas, MCP safety annotations, stable receipts, explicit limits and refusal semantics |
| Exhaustive claims are real | Server-owned pagination traversal; caller cannot upload evidence; any failed obligation blocks certification |

## Quality evidence

### Real agent and user value

APIVouch completes a task that a prompt cannot reliably complete: it calls independent providers, validates the returned outcomes, rejects disagreement and constraint violations, and issues a commit-bound integrity receipt. Its provider-qualification lab also inspects documented APIs repeatedly, detects runtime drift, and serves derived tools through MCP.

### Demonstrated capability quality

- The real-data demo resolves one USD→EUR reference rate across three independently operated public origins and requires two schema-valid values within 2% tolerance.
- The first self-contained demo routes four provider fixtures, rejects a schema failure and an HTTP failure, selects only from the agreeing pair, then re-verifies the stored receipt.
- Normal REST and MCP requests require distinct configured and post-redirect network origins; the demo bypass is explicit in its receipt.
- The provider-qualification demo supplies deterministic OpenAPI test conditions without a third-party API.
- Every observation records status, latency, content type, JSON validity, schema validity, and a bounded payload sample.
- Findings distinguish missing documentation from observed runtime mismatch.
- The generated contract records the basis of every inserted change.
- Export contains the contract, observations, findings, tool schemas, comparison, and endpoint.
- The demo certifies seven catalog records across three pages, and the same verifier is callable as REST and MCP.

### Engineering and maintainability

- 47 unit and REST/MCP integration tests, including disagreement, budget, receipt-tampering, origin-independence, bounded previews, and adversarial pagination-proof cases.
- Ruff, Python compilation, JavaScript syntax, YAML parsing, secret-pattern, file-count, and size checks.
- REST and MCP calls share one runtime and error model.
- No LLM or vendor API is required.
- CI builds the production Docker image after all code checks.

### MCP productization readiness

- Product and generated-project JSON-RPC endpoints implement `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call`.
- Generated inputs and outputs use JSON Schema.
- Tools carry read-only, destructive, idempotent, and open-world annotations.
- Invalid arguments, authentication errors, rate limits, upstream failures, invalid JSON, schema mismatch, and confirmation requirements have stable codes.

### Adoption and operation

- One-container deployment and same-origin dashboard/API.
- Free self-contained demo and downloadable evidence pack.
- Atomic paid unit: one Verified Outcome selected under caller-provided cost and latency limits.
- The current demo makes no false settlement claim; x402 settlement is a documented post-verification integration point.
- Clear expansion path: x402 settlement, scheduled drift monitoring, retained history, private credentials, team access control, and outcome SLAs.

## Exact verification commands

```bash
ruff check backend
python -m compileall -q backend/app
python -m pytest -q
node --check frontend/app.js
docker build -t apivouch:review .
```

After deployment, follow `docs/demo.md`, then run the official X-Agent offline and online validators against the submission directory.
