# APIVouch — X-Agent MCP Hackathon submission draft

## Track

General Challenge (Open Innovation).

APIVouch is agent reliability infrastructure, not an on-chain security or
auditing product. Its callable task is to resolve one API-backed outcome from
independent providers while enforcing schema, origin, price, latency, and
agreement constraints.

## One-line capability

APIVouch routes an agent goal across independent public APIs, rejects invalid
or disagreeing evidence, and returns one constraint-bound outcome with a stored,
tamper-evident receipt that the agent can re-verify through MCP.

## Why an agent uses it

An agent cannot safely act on the first API response when a provider may be
down, over budget, schema-invalid, redirected to the same origin, or disagreeing
with independent sources. APIVouch turns those uncertainties into a deterministic
`VERIFIED` or `UNVERIFIED` result and preserves the decision evidence.

## Verifiable call

```bash
python scripts/verify_hackathon.py --live
```

This initializes the MCP server, lists the public tools, calls three independent
public exchange-rate providers, stores the resulting receipt, re-verifies its
SHA-256 integrity through MCP, and checks that the health and deployment-proof
endpoints report the same source commit.

For a network-independent reviewer check:

```bash
python scripts/verify_hackathon.py
```

## MCP surface

- `apivouch_resolve_verified_outcome`: call 2–5 independent providers and issue
  a constraint-bound evidence receipt.
- `apivouch_verify_receipt`: retrieve a stored receipt and recompute its
  integrity fingerprint.

Streamable HTTP / JSON-RPC endpoint: `POST /mcp`.

## Safety and data declaration

- Caller-supplied providers must use distinct HTTP(S) network origins.
- Redirects are checked again for origin independence.
- Private, loopback, link-local, and cloud-metadata targets are blocked by
  default.
- Query-string values are redacted from receipts; full request URLs are stored
  only as SHA-256 digests.
- Response bodies are represented by digests and bounded scalar previews.
- No customer API credentials are stored.
- Price is a transparent quote; this release does not move payment.
- The deterministic fixture is explicitly labelled and separate from the live
  public-provider demonstration.

## Monetization

Free calls can verify public, zero-cost providers. A paid hosted tier can charge
per verified outcome rather than per attempted provider call, with higher plans
for longer receipt retention, private provider connectors, organization policy,
SLA monitoring, and signed evidence exports. The current release reports quoted
provider costs but deliberately performs no settlement.

## Required values before packaging the official PR

- Public deployment URL: **pending**
- Health URL: `<deployment>/health`
- Deployment proof: `<deployment>/.well-known/xagent-verification.json`
- Exact 40-character reviewed commit: **pending until final push**
- Public source repository: `https://github.com/sklabstudio/apivouch`

Do not replace the pending fields until the deployed service returns the exact
same commit from both proof endpoints.
