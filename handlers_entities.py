"""Brevo contacts, lists, email campaigns, and transactional email handlers."""
from __future__ import annotations
from imperal_sdk import ActionResult
import brevo_client as br
from app import chat
from handlers_connection import resolve_or_error
from schemas import (
    ListContactsParams, Contact, ContactList, CreateContactParams, ContactResult,
    ListListsParams, MailingList, MailingListList, CreateListParams, ListResult,
    ListCampaignsParams, Campaign, CampaignList, CreateCampaignParams, CampaignResult,
    SendTransactionalEmailParams, TransactionalEmailResult,
)

def _error(exc: br.ClientFail) -> ActionResult:
    return ActionResult.error(exc.payload["message"], code=exc.payload["code"])

@chat.function("list_contacts", "List contacts in the connected Brevo account.", action_type="read", chain_callable=True, data_model=ContactList)
async def list_contacts(ctx, params: ListContactsParams) -> ActionResult:
    """Retrieve a bounded page of contacts."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try:
        data = await br.request(conn["api_key"], "GET", "/contacts", params={"limit": params.limit}, action="list contacts")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(ContactList(contacts=[Contact(email=x.get("email", ""), id=x.get("id", 0), attributes=x.get("attributes", {})) for x in data.get("contacts", [])]), summary="Contacts listed.")

@chat.function("create_contact", "Create or update a Brevo contact, optionally adding it to existing lists.", action_type="write", chain_callable=True, effects=["create:contact"], event="brevo-connector.create_contact", data_model=ContactResult)
async def create_contact(ctx, params: CreateContactParams) -> ActionResult:
    """Create a contact through Brevo's contacts endpoint."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    body = {"email": params.email, "attributes": params.attributes, "listIds": params.list_ids, "updateEnabled": True}
    try:
        data = await br.request(conn["api_key"], "POST", "/contacts", json_body=body, action="create contact")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(ContactResult(id=data.get("id", 0), email=params.email), summary="Contact created.")

@chat.function("list_mailing_lists", "List audience lists in the connected Brevo account.", action_type="read", chain_callable=True, data_model=MailingListList)
async def list_mailing_lists(ctx, params: ListListsParams) -> ActionResult:
    """Retrieve a bounded page of Brevo lists."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try:
        data = await br.request(conn["api_key"], "GET", "/contacts/lists", params={"limit": params.limit}, action="list lists")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(MailingListList(lists=[MailingList(id=x.get("id", 0), name=x.get("name", ""), total_blacklisted=x.get("totalBlacklisted", 0), total_subscribers=x.get("totalSubscribers", 0)) for x in data.get("lists", [])]), summary="Mailing lists listed.")

@chat.function("create_mailing_list", "Create a new Brevo contact list.", action_type="write", chain_callable=True, effects=["create:list"], event="brevo-connector.create_mailing_list", data_model=ListResult)
async def create_mailing_list(ctx, params: CreateListParams) -> ActionResult:
    """Create an audience list."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try:
        data = await br.request(conn["api_key"], "POST", "/contacts/lists", json_body={"name": params.name, "folderId": params.folder_id}, action="create list")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(ListResult(id=data.get("id", 0), name=params.name), summary="Mailing list created.")

@chat.function("list_campaigns", "List email campaigns in the connected Brevo account.", action_type="read", chain_callable=True, data_model=CampaignList)
async def list_campaigns(ctx, params: ListCampaignsParams) -> ActionResult:
    """Retrieve a bounded page of email campaigns."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    try:
        data = await br.request(conn["api_key"], "GET", "/emailCampaigns", params={"limit": params.limit}, action="list campaigns")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(CampaignList(campaigns=[Campaign(id=x.get("id", 0), name=x.get("name", ""), status=x.get("status", ""), type=x.get("type", ""), sent_date=x.get("sentDate", "")) for x in data.get("campaigns", [])]), summary="Campaigns listed.")

@chat.function("create_campaign", "Create a draft Brevo email campaign for specified existing lists; it is not sent automatically.", action_type="write", chain_callable=True, effects=["create:campaign"], event="brevo-connector.create_campaign", data_model=CampaignResult)
async def create_campaign(ctx, params: CreateCampaignParams) -> ActionResult:
    """Create a campaign draft; sending remains a deliberate provider-side action."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    body = {"name": params.name, "subject": params.subject, "sender": {"name": params.sender_name, "email": params.sender_email}, "htmlContent": params.html_content, "recipients": {"listIds": params.recipient_list_ids}}
    try:
        data = await br.request(conn["api_key"], "POST", "/emailCampaigns", json_body=body, action="create campaign")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(CampaignResult(id=data.get("id", 0), name=params.name), summary="Campaign created.")

@chat.function("send_transactional_email", "Send one transactional email through Brevo to an explicit recipient.", action_type="write", chain_callable=True, effects=["send:email"], event="brevo-connector.send_transactional_email", data_model=TransactionalEmailResult)
async def send_transactional_email(ctx, params: SendTransactionalEmailParams) -> ActionResult:
    """Send a single explicitly addressed transactional message."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err: return err
    body = {"sender": {"email": params.sender_email, "name": params.sender_name}, "to": [{"email": params.to_email, "name": params.to_name}], "subject": params.subject, "htmlContent": params.html_content}
    try:
        data = await br.request(conn["api_key"], "POST", "/smtp/email", json_body=body, action="send transactional email")
    except br.ClientFail as exc: return _error(exc)
    return ActionResult.success(TransactionalEmailResult(message_id=data.get("messageId", "")), summary="Transactional email send requested.")
