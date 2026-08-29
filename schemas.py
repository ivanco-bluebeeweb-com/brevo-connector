"""Pydantic models for Brevo Connector."""
from pydantic import BaseModel, Field

class NoParams(BaseModel): pass
class Scoped(BaseModel):
    connection_id: str = Field("", description="Saved Brevo account id; omit when only one account is connected.")

class ConnectBrevoParams(BaseModel):
    label: str = Field("", description="Friendly label, e.g. Marketing workspace.")
    api_key: str = Field(description="Brevo API key from SMTP & API > API Keys.")
class ConnectionResult(BaseModel):
    connection_id: str = ""
    label: str = ""
class DisconnectParams(BaseModel): connection_id: str
class Connection(BaseModel): id: str = ""; label: str = ""; email: str = ""
class ConnectionList(BaseModel): connections: list[Connection] = Field(default_factory=list)
class DeleteResult(BaseModel): deleted: bool = False; id: str = ""

class ListContactsParams(Scoped):
    limit: int = Field(20, ge=1, le=100)
class Contact(BaseModel): email: str = ""; id: int = 0; attributes: dict = Field(default_factory=dict)
class ContactList(BaseModel): contacts: list[Contact] = Field(default_factory=list)
class CreateContactParams(Scoped):
    email: str
    attributes: dict = Field(default_factory=dict, description="Contact attributes, e.g. {'FIRSTNAME':'Ada'}.")
    list_ids: list[int] = Field(default_factory=list, description="Optional existing Brevo list IDs.")
class ContactResult(BaseModel): id: int = 0; email: str = ""

class ListListsParams(Scoped):
    limit: int = Field(20, ge=1, le=50)
class MailingList(BaseModel): id: int = 0; name: str = ""; total_blacklisted: int = 0; total_subscribers: int = 0
class MailingListList(BaseModel): lists: list[MailingList] = Field(default_factory=list)
class CreateListParams(Scoped): name: str
class ListResult(BaseModel): id: int = 0; name: str = ""

class ListCampaignsParams(Scoped):
    limit: int = Field(20, ge=1, le=100)
class Campaign(BaseModel): id: int = 0; name: str = ""; status: str = ""; type: str = ""; sent_date: str = ""
class CampaignList(BaseModel): campaigns: list[Campaign] = Field(default_factory=list)
class CreateCampaignParams(Scoped):
    name: str
    subject: str
    sender_name: str
    sender_email: str
    html_content: str
    recipient_list_ids: list[int] = Field(description="Existing Brevo list IDs to receive this campaign.")
class CampaignResult(BaseModel): id: int = 0; name: str = ""

class SendTransactionalEmailParams(Scoped):
    sender_email: str
    sender_name: str = ""
    to_email: str
    to_name: str = ""
    subject: str
    html_content: str
class TransactionalEmailResult(BaseModel): message_id: str = ""

class AuditBrevoAccountParams(Scoped): pass
class BrevoAccountReport(BaseModel):
    email: str = ""
    company_name: str = ""
    plan: list[dict] = Field(default_factory=list)
    total_contacts: int = 0
    total_lists: int = 0
    total_campaigns: int = 0
