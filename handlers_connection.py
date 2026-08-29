"""Brevo account connection lifecycle."""
from __future__ import annotations
import json
import uuid
from imperal_sdk import ActionResult
import brevo_client as br
from app import chat
from schemas import ConnectBrevoParams, ConnectionResult, DisconnectParams, DeleteResult, Connection, ConnectionList, NoParams

_SECRET = "brevo_connections"

async def _load(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    try:
        value = json.loads(raw) if raw else []
    except (TypeError, ValueError):
        value = []
    return value if isinstance(value, list) else []

async def _save(ctx, items: list[dict]) -> None:
    await ctx.secrets.set(_SECRET, json.dumps(items))

async def resolve(ctx, connection_id: str = "") -> dict | None:
    items = await _load(ctx)
    if connection_id:
        return next((item for item in items if item.get("id") == connection_id), None)
    return items[0] if items else None

async def resolve_or_error(ctx, connection_id: str = ""):
    item = await resolve(ctx, connection_id)
    if not item:
        return None, ActionResult.error("No Brevo account found. Connect one with connect_brevo first.", code=br.BR_NOT_CONNECTED)
    return item, None

@chat.function("connect_brevo", "Connect Brevo using an API key after verifying it against the account endpoint.", action_type="write", chain_callable=True, effects=["create:connection"])
async def connect_brevo(ctx, params: ConnectBrevoParams) -> ActionResult:
    """Verify the supplied API key then store it in the encrypted secret store."""
    try:
        account = await br.request(params.api_key, "GET", "/account", action="verify API key")
    except br.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    connection_id = str(uuid.uuid4())
    items = await _load(ctx)
    items.append({
        "id": connection_id, "label": params.label or account.get("companyName") or "Brevo account",
        "email": account.get("email", ""), "api_key": params.api_key,
    })
    await _save(ctx, items)
    return ActionResult.ok(ConnectionResult(connection_id=connection_id, label=items[-1]["label"]))

@chat.function("disconnect_brevo", "Disconnect a Brevo account and delete only its locally saved API key.", action_type="write", chain_callable=True, effects=["delete:connection"])
async def disconnect_brevo(ctx, params: DisconnectParams) -> ActionResult:
    """Forget one saved Brevo credential without changing the Brevo account."""
    items = await _load(ctx)
    remaining = [item for item in items if item.get("id") != params.connection_id]
    if len(remaining) == len(items):
        return ActionResult.error("That Brevo connection was not found.", code=br.BR_NOT_FOUND)
    await _save(ctx, remaining)
    return ActionResult.ok(DeleteResult(deleted=True, id=params.connection_id))

@chat.function("list_connections", "List saved Brevo accounts without exposing their API keys.", action_type="read", chain_callable=True, data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """Return safe connection metadata only."""
    return ActionResult.ok(ConnectionList(connections=[Connection(id=x.get("id", ""), label=x.get("label", ""), email=x.get("email", "")) for x in await _load(ctx)]))
