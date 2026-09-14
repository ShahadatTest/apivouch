"""Verify an APIVouch receipt offline using only Python's standard library."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def fingerprint(receipt: dict[str, Any]) -> str:
    body = dict(receipt)
    body.pop("integrity", None)
    body.pop("receipt_id", None)
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def verify(receipt: dict[str, Any]) -> bool:
    expected = fingerprint(receipt)
    return (
        (receipt.get("integrity") or {}).get("fingerprint") == expected
        and receipt.get("receipt_id") == expected.split(":", 1)[1][:24]
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python examples/verify_outcome_receipt.py RECEIPT.json", file=sys.stderr)
        return 2
    receipt = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    valid = verify(receipt)
    print(json.dumps({"receipt_id": receipt.get("receipt_id"), "integrity_valid": valid}))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
