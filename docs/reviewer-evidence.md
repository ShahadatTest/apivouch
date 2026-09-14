# Reviewer evidence map

This document points to evidence; it does not assign a score or claim acceptance.

## Hard gates

| Gate | Evidence after deployment |
|---|---|
| Callable | Root workbench, `/docs`, project REST API, and `/mcp/{project_id}` |
| Version-bound | `/health` and `/.well-known/xagent-verification.json` return the deployed 40-character commit |
| Reproducible | Pinned dependencies, root Dockerfile, Docker Compose, Render blueprint, exact test/run commands |
| Safe to evaluate | Read-only automatic boundary, structured errors, bounded network calls, SSRF checks, no accepted/stored credentials |
| Useful for agents | JSON Schemas, MCP safety annotations, stable result envelope, explicit limits and error semantics |
| Exhaustive claims are real | Server-owned pagination traversal; caller cannot upload evidence; any failed obligation blocks certification |

## Quality evidence

### Real agent and user value

APIVouch completes a task that a prompt cannot reliably complete: it calls a documented API repeatedly, records runtime observations, validates them against the declared contract, detects shape drift, and serves the derived tools through MCP.

### Demonstrated capability quality

- Self-contained demo supplies deterministic test conditions without a third-party API.
- Every observation records status, latency, content type, JSON validity, schema validity, and a bounded payload sample.
- Findings distinguish missing documentation from observed runtime mismatch.
- The generated contract records the basis of every inserted change.
- Export contains the contract, observations, findings, tool schemas, comparison, and endpoint.
- The demo certifies seven catalog records across three pages, and the same verifier is callable as REST and MCP.

### Engineering and maintainability

- 38 unit and REST/MCP integration tests, including adversarial proof cases.
- Ruff, Python compilation, JavaScript syntax, YAML parsing, secret-pattern, file-count, and size checks.
- REST and MCP calls share one runtime and error model.
- No LLM or vendor API is required.
- CI builds the production Docker image after all code checks.

### MCP productization readiness

- Stateless JSON-RPC endpoint implements `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call`.
- Generated inputs and outputs use JSON Schema.
- Tools carry read-only, destructive, idempotent, and open-world annotations.
- Invalid arguments, authentication errors, rate limits, upstream failures, invalid JSON, schema mismatch, and confirmation requirements have stable codes.

### Adoption and operation

- One-container deployment and same-origin dashboard/API.
- Free self-contained demo and downloadable evidence pack.
- Atomic paid unit: one Agent Readiness Evidence Pack.
- Clear expansion path: scheduled drift monitoring, retained history, private credentials, team access control, and alerts.

## Exact verification commands

```bash
ruff check backend
python -m compileall -q backend/app
python -m pytest -q
node --check frontend/app.js
docker build -t apivouch:review .
```

After deployment, follow `docs/demo.md`, then run the official X-Agent offline and online validators against the submission directory.
