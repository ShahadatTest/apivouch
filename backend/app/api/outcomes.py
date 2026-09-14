from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas.api import OutcomeRequest
from app.services.outcomes import (
    execute_verified_outcome,
    load_receipt,
    store_receipt,
    verify_receipt,
)

router = APIRouter(prefix="/outcomes", tags=["verified outcomes"])


async def run_and_store(body: OutcomeRequest) -> dict:
    try:
        receipt = await execute_verified_outcome(body.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    store_receipt(receipt)
    return receipt


@router.post("/execute")
async def execute(body: OutcomeRequest):
    """Resolve one outcome across independent providers and issue an integrity receipt."""
    return await run_and_store(body)


@router.post("/demo")
async def demo(request: Request):
    base = str(request.base_url).rstrip("/")
    expected = {"type": "number", "minimum": 0}
    body = OutcomeRequest.model_validate(
        {
            "goal": "Get a verified same-day delivery quote for parcel DEMO-42",
            "providers": [
                {"name": "Atlas Courier", "url": f"{base}/demo/providers/atlas", "result_path": "quote.amount_usd", "expected_schema": expected, "price_usd": 0.004},
                {"name": "Beacon Logistics", "url": f"{base}/demo/providers/beacon", "result_path": "quote.amount_usd", "expected_schema": expected, "price_usd": 0.003},
                {"name": "Legacy Ship", "url": f"{base}/demo/providers/legacy", "result_path": "quote.amount_usd", "expected_schema": expected, "price_usd": 0.001},
                {"name": "Offline Express", "url": f"{base}/demo/providers/offline", "result_path": "quote.amount_usd", "expected_schema": expected, "price_usd": 0.002},
            ],
            "constraints": {"max_price_usd": 0.01, "max_latency_ms": 3000, "minimum_agreement": 2, "numeric_tolerance_percent": 1},
        }
    )
    receipt = await execute_verified_outcome(body.model_dump(), require_independent_origins=False)
    store_receipt(receipt)
    return receipt


@router.get("/receipts/{receipt_id}")
async def receipt(receipt_id: str):
    value = load_receipt(receipt_id)
    if not value:
        raise HTTPException(404, "Receipt not found")
    return {"receipt": value, "integrity_valid": verify_receipt(value)}
