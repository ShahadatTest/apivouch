from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx

from app.core.config import MAX_REDIRECTS, MAX_RESPONSE_BYTES, REQUEST_TIMEOUT
from app.core.security import validate_url_for_fetch


@dataclass
class SafeResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes
    url: str

    def json(self) -> Any:
        import json

        return json.loads(self.content.decode("utf-8", errors="strict"))


async def safe_request(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    json_body: Any = None,
) -> SafeResponse:
    """Make a bounded request while validating every redirect target."""
    current = validate_url_for_fetch(url)
    request_method = method.upper()
    for redirect_number in range(MAX_REDIRECTS + 1):
        validate_url_for_fetch(current)
        async with (
            httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=False) as client,
            client.stream(
                request_method,
                current,
                params=params if redirect_number == 0 else None,
                headers=headers,
                json=json_body if redirect_number == 0 else None,
            ) as response,
        ):
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError(f"Response exceeds {MAX_RESPONSE_BYTES} bytes")
            response_headers = {key.lower(): value for key, value in response.headers.items()}
            status = response.status_code
        if status not in {301, 302, 303, 307, 308}:
            return SafeResponse(status, response_headers, bytes(body), current)
        location = response_headers.get("location")
        if not location:
            return SafeResponse(status, response_headers, bytes(body), current)
        if redirect_number >= MAX_REDIRECTS:
            raise ValueError("Too many redirects")
        current = validate_url_for_fetch(urljoin(current, location))
        if status == 303:
            request_method = "GET"
    raise ValueError("Redirect handling failed")
