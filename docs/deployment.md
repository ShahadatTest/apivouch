# Deployment and release verification

## Render blueprint

`render.yaml` deploys the root multi-stage Dockerfile and a PostgreSQL database.
Render supplies `RENDER_GIT_COMMIT`; APIVouch exposes that exact value from both
required proof endpoints.

1. Push the final reviewed commit to the public repository.
2. Create or refresh the Render Blueprint from `render.yaml`.
3. Keep `ALLOW_PRIVATE_NETWORK=false`.
4. Wait for the Docker build, its 49-test gate, and the health check to pass.
5. Record the public HTTPS origin without a trailing slash.

## Mandatory release check

```bash
API_ORIGIN=https://your-service.example
curl --fail "$API_ORIGIN/health"
curl --fail "$API_ORIGIN/.well-known/xagent-verification.json"
curl --fail -X POST "$API_ORIGIN/api/outcomes/live-demo"
curl --fail -X POST "$API_ORIGIN/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

The two proof endpoints must return the same exact 40-character commit that is
submitted to the hackathon. The live demo must return `VERIFIED`; if fewer than
two public providers agree, retain the honest `UNVERIFIED` result and rerun only
after diagnosing provider availability.

## Local container check

```bash
docker compose build --pull
docker compose up -d
docker compose ps
python scripts/verify_hackathon.py --live
docker compose down
```

The final image runs as UID `10001`, includes only production dependencies, and
has an HTTP healthcheck. The test toolchain exists only in the intermediate
build stage.
