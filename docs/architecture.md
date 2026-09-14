# Architecture

```text
OpenAPI URL / JSON / YAML
        │
        ├─ bounded fetch + SSRF/redirect checks
        ▼
local-ref resolver + operation extractor
        │
        ├─ deterministic static analyzer
        ├─ safe repeated live probes
        ├─ JSON/content-type/schema validation
        └─ response-shape drift evidence
        ▼
evidence-labelled agent contract
        │
        ├─ re-analysis (real before/after score)
        ├─ JSON Schema MCP tool definitions
        ├─ stable runtime result envelope
        ├─ server-owned exhaustive pagination proof
        └─ stateless JSON-RPC MCP endpoint
```

## Trust boundaries

The imported API remains an untrusted external system. APIVouch never installs code from a contract, executes generated code, accepts embedded URL credentials, or automatically invokes state-changing methods.

The proof caller is also untrusted. It may state a claim and ordinary operation arguments, but it cannot send observed records, counts, cursors, page state, totals, or snapshots. APIVouch collects those facts directly. Any broken pagination, inconsistent total, changed snapshot, repeated page/cursor, or collection cap is a blocking obligation, so `PROVEN` cannot coexist with failed evidence.

The generated contract is a derived artifact. Every inserted field is marked with `x-apivouch-generated` where applicable, and the exported change list records its evidence basis.

## Storage

The compact review deployment uses one SQLAlchemy `projects` table with JSON documents for the source specification, analysis, live observations, findings, score, generated contract/change bundle, tools, and comparison.

This keeps the review artifact reproducible. Production multi-tenant operation should use PostgreSQL, access control, quotas, project ownership, and expiry policies.

## Transport

The REST API manages projects and evidence. Each project also becomes a stateless MCP server at `/mcp/{project_id}`. REST proxy calls and MCP `tools/call` share the same runtime, validation, error envelope, and read-only boundary. REST and MCP exhaustiveness calls share the same bounded collector and verifier.

## Network controls

Every initial URL and redirect target is checked. The service blocks credentials in URLs and production access to loopback, private, link-local, metadata, multicast, reserved, or unspecified addresses. Response bytes, redirects, timeouts, retries, project count, operation count, upload size, proof pages, and proof records are bounded.
