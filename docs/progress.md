# Release status

## Completed for 1.1

- Deterministic OpenAPI 3.x / Swagger 2.0 import and local-reference resolution
- Six-dimension readiness analysis with structured findings
- Bounded repeat live probes with required-argument handling
- JSON, content-type, status, and response-schema validation
- Successful-response shape-drift detection
- Evidence-labelled agent contract generation
- Real source-versus-contract re-analysis; all simulated score logic removed
- JSON Schema tool generation with MCP safety annotations
- Stateless JSON-RPC MCP `initialize`, `tools/list`, and `tools/call`
- One runtime for REST and MCP invocation with stable errors
- Redirect-aware SSRF controls and body/timeout/retry limits
- Self-contained live demo and responsive reviewer workbench
- Single-image Docker deployment and Render blueprint
- Unit plus REST/MCP integration tests
- Server-owned Exhaustiveness Gate for `ALL`, `NONE`, `EXACT_COUNT`, `MIN`, and `MAX`
- Cursor, page, and offset traversal with page/record caps
- Snapshot, total, repeated-page, repeated-cursor, and partial-start checks
- Content-addressed proof certificates through both REST and MCP

## Account-level release steps

- Deploy the final public commit.
- Confirm `/health` and `/.well-known/xagent-verification.json` report that exact 40-character commit.
- Update the existing X-Agent submission package and PR with the final source, URL, commit, and verification transcript.
- Keep the public service reachable throughout review.
