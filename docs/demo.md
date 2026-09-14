# Reviewer demo

## One-click path

1. Open the deployed root page.
2. Choose **Run self-contained live demo**.
3. APIVouch imports its deliberately incomplete Shop API contract.
4. It makes three bounded calls to each safe operation.
5. The evidence table shows response-shape drift for weather and product data.
6. It generates an evidence-labelled agent contract.
7. Open **MCP tools** and **Connect** to inspect the real tool schemas and project MCP URL.
8. Open **Exhaustiveness proof**: the demo has already traversed three catalog pages and certified exactly seven records.
9. Try `MAX`, field `price`, candidate `p2` to prove the highest-priced item using the same server-owned evidence flow.
10. Export the full evidence pack.

The expected local reference result is approximately 54/100 for the source and 82/100 for the generated contract. Scores can change when scoring rules or the deliberately inconsistent demo contract change; the response itself is authoritative.

## Manual API path

```bash
curl http://localhost:8000/demo/openapi.json
```

Post that object as `openapi_json` to `POST /api/projects`, then call:

```text
POST /api/projects/{id}/test       {"samples_per_endpoint":3}
POST /api/projects/{id}/contract   {}
POST /api/projects/{id}/prove      {"operation_id":"listItems","claim_type":"EXACT_COUNT","expected_count":7,"arguments":{"limit":3}}
POST /mcp/{id}                     {"jsonrpc":"2.0","id":1,"method":"tools/list"}
GET  /api/projects/{id}/export
```

## Negative evidence

The demo intentionally proves that APIVouch does not hide upstream variability. Different successful JSON shapes become `OBSERVED_SHAPE_DRIFT`; the generated schema represents the observed union and the MCP runtime provides a stable outer result envelope.

It also demonstrates positive proof under a stable `demo-catalog-v1` snapshot. The collector receives page sizes only; all returned items, cursors, totals, and snapshot evidence come from the demo API itself.
