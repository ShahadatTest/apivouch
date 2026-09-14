# Security policy

## Supported version

The latest commit on `main` is the supported review version during the
hackathon. Deployment and source must be bound by the exact commit returned by
`/health` and `/.well-known/xagent-verification.json`.

## Reporting a vulnerability

Do not open a public issue containing an exploit, credential, private endpoint,
or customer data. Use GitHub's private vulnerability reporting for this
repository. If that channel is unavailable, open a public issue requesting a
private contact channel without including sensitive details.

## Security boundaries

- APIVouch accepts credential-free public provider URLs in the current release.
- Credentials embedded in URLs are rejected.
- Private, loopback, link-local, metadata, multicast, reserved, and unspecified
  targets are blocked by default, including after redirects.
- Automatic provider and generated-tool calls are limited to read-only HTTP
  methods; state-changing operations require explicit confirmation elsewhere.
- Network concurrency, timeouts, retries, redirects, response bytes, project
  count, endpoint count, proof pages, and proof records are bounded.
- Receipt URLs redact query values, payloads are content-digested, and only
  bounded scalar previews are retained.

## Deployment guidance

Keep `ALLOW_PRIVATE_NETWORK=false` in public deployments. Use PostgreSQL,
authentication, tenant isolation, quotas, and retention policies before storing
customer evidence. Rotate any credential that is accidentally exposed and do
not include it in a vulnerability report.
