"""Read-only account overview for Brevo Connector."""
from __future__ import annotations
from imperal_sdk import ActionResult
import brevo_client as br
from app import chat
from handlers_connection import resolve_or_error
from schemas import AuditBrevoAccountParams, BrevoAccountReport

@chat.function(
    "audit_brevo_account",
    "Build an aggregated Brevo account overview: account identity, plans, contacts, lists, and campaigns.",
    action_type="read", chain_callable=True, data_model=BrevoAccountReport,
)
async def audit_brevo_account(ctx, params: AuditBrevoAccountParams) -> ActionResult:
    """Read account and collection totals without changing Brevo data."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        account = await br.request(conn["api_key"], "GET", "/account", action="read account")
        contacts = await br.request(conn["api_key"], "GET", "/contacts", params={"limit": 1}, action="count contacts")
        lists = await br.request(conn["api_key"], "GET", "/contacts/lists", params={"limit": 1}, action="count lists")
        campaigns = await br.request(conn["api_key"], "GET", "/emailCampaigns", params={"limit": 1}, action="count campaigns")
    except br.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    return ActionResult.success(BrevoAccountReport(
        email=account.get("email", ""), company_name=account.get("companyName", ""),
        plan=account.get("plan", []),
        total_contacts=int(contacts.get("count", 0)),
        total_lists=int(lists.get("count", 0)),
        total_campaigns=int(campaigns.get("count", 0)),
    ), summary="Brevo account audit ready.")
