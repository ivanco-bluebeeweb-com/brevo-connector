"""Small HTTP client for Brevo API v3 using a user-owned API key."""
from __future__ import annotations
from typing import Any
import httpx

BASE_URL = "https://api.brevo.com/v3"
BR_NOT_CONNECTED = "BREVO_NOT_CONNECTED"
BR_UNAUTHORIZED = "BREVO_UNAUTHORIZED"
BR_FORBIDDEN = "BREVO_FORBIDDEN"
BR_NOT_FOUND = "BREVO_NOT_FOUND"
BR_RATE_LIMITED = "BREVO_RATE_LIMITED"
BR_BACKEND_ERROR = "BREVO_BACKEND_ERROR"
BR_VALIDATION_FAILED = "BREVO_VALIDATION_FAILED"
BR_RESPONSE_UNEXPECTED = "BREVO_RESPONSE_UNEXPECTED"
_MESSAGES = {
    BR_NOT_CONNECTED: "No Brevo account is connected. Connect one first.",
    BR_UNAUTHORIZED: "Brevo rejected the API key as invalid or expired.",
    BR_FORBIDDEN: "Brevo denied access to this resource.",
    BR_NOT_FOUND: "That Brevo record was not found.",
    BR_RATE_LIMITED: "Brevo rate-limited this request. Try again shortly.",
    BR_BACKEND_ERROR: "Brevo returned an error.",
    BR_VALIDATION_FAILED: "Brevo rejected the request as invalid.",
    BR_RESPONSE_UNEXPECTED: "Brevo returned an unexpected response.",
}

def fail(code: str, detail: str = "") -> dict:
    message = _MESSAGES.get(code, "Brevo request failed.")
    return {"code": code, "message": f"{message} ({detail})" if detail else message}

class ClientFail(Exception):
    def __init__(self, payload: dict):
        super().__init__(payload["message"])
        self.payload = payload

def _status_code(status: int) -> str:
    if status == 401: return BR_UNAUTHORIZED
    if status == 403: return BR_FORBIDDEN
    if status == 404: return BR_NOT_FOUND
    if status == 429: return BR_RATE_LIMITED
    if status >= 500: return BR_BACKEND_ERROR
    return BR_VALIDATION_FAILED

async def request(api_key: str, method: str, path: str, *, params: dict | None = None,
                  json_body: Any = None, action: str = "") -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method, f"{BASE_URL}{path}", params=params, json=json_body,
            headers={"api-key": api_key, "accept": "application/json", "content-type": "application/json"},
        )
    if response.status_code >= 400:
        raise ClientFail(fail(_status_code(response.status_code), f"{action}: HTTP {response.status_code}: {response.text[:250]}"))
    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise ClientFail(fail(BR_RESPONSE_UNEXPECTED, response.text[:250])) from exc
