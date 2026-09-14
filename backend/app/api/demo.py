from __future__ import annotations

from itertools import count

from fastapi import APIRouter, Request

router = APIRouter(prefix="/demo")
_weather_calls = count()
_product_calls = count()


@router.get("/openapi.json", include_in_schema=False)
async def demo_openapi(request: Request):
    base = str(request.base_url).rstrip("/") + "/demo"
    return {
        "openapi": "3.0.3",
        "info": {"title": "Deliberately Inconsistent Shop API", "version": "0.1.0"},
        "servers": [{"url": base}],
        "paths": {
            "/weather": {"get": {"summary": "Weather", "parameters": [{"name": "q", "in": "query"}], "responses": {"200": {"description": "ok"}}}},
            "/product": {"get": {"operationId": "getProduct", "responses": {"200": {"description": "ok"}}}},
            "/user": {"get": {"operationId": "getUser", "summary": "Get user profile", "responses": {"200": {"description": "ok"}}}},
        },
    }


@router.get("/weather", include_in_schema=False)
async def weather():
    if next(_weather_calls) % 2:
        return {"temperature": 31, "weather": "sunny"}
    return {"tmp": "31 C", "desc": "sun"}


@router.get("/product", include_in_schema=False)
async def product():
    price = 149.99 if next(_product_calls) % 2 else "149.99"
    return {"name": "Lamp", "price": price}


@router.get("/user", include_in_schema=False)
async def user():
    return {"id": 1, "name": None, "email": "demo@example.com"}
