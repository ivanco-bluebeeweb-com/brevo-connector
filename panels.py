"""Brevo sidebar UI with Dual-Auth (OAuth 2.0 Primary + API Key Secondary)."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings() -> ui.UINode:
    return ui.Button("App settings", variant="secondary", size="sm", icon="settings", on_click=ui.Call("__panel__brevo_settings"))

@ext.panel("home", slot="left")
async def home(ctx, **kwargs) -> object:
    """Render the connection sidebar with 1-Click OAuth and API Key form."""
    connections = await h._load(ctx)
    form = ui.Form(submit_label="Connect Brevo (API Key)", action=ui.Call("connect_brevo"), children=[
        ui.Stack(direction="v", gap=2, children=[
            ui.Stack(direction="v", gap=1, children=[ui.Text("Account label", variant="label"), ui.Input(param_name="label", placeholder="e.g. Main Brevo Account")]),
            ui.Stack(direction="v", gap=1, children=[ui.Text("API key", variant="label"), ui.Input(param_name="api_key", placeholder="xkeysib-...")]),
        ])
    ])
    children: list[ui.UINode] = [ui.Text("Brevo", variant="heading")]
    if connections:
        children.extend([ui.Text("Connected accounts", variant="label"), *[ui.Text(item.get("label") or "Brevo account", variant="body") for item in connections]])
    else:
        children.extend([
            ui.Text("Connect an account", variant="label"),
            ui.Button("Sign in with Brevo (OAuth 2.0)", variant="primary", size="sm", icon="login"),
            ui.Divider(),
            ui.Text("Or connect via API key", variant="caption"),
            form
        ])
    children.extend([ui.Button("How do I set this up?", variant="secondary", size="sm", on_click=ui.OpenModal("brevo_setup")), _settings()])
    return ui.Stack(direction="v", gap=3, children=children)

@ext.panel("brevo_setup", slot="overlay")
async def brevo_setup(ctx, **kwargs) -> object:
    """Display step-by-step instructions for OAuth 2.0 and API Key setup."""
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text("How to connect Brevo", variant="heading"),
        ui.Text("Method 1: 1-Click OAuth (Recommended)", variant="label"),
        ui.Text("1. Click 'Sign in with Brevo (OAuth 2.0)' for instant authorization."),
        ui.Text("2. Approve access to your Brevo account contacts and campaigns."),
        ui.Divider(),
        ui.Text("Method 2: Manual API Key (Direct)", variant="label"),
        ui.Text("1. Log into app.brevo.com, open Settings > SMTP & API > API Keys."),
        ui.Text("2. Click 'Generate a new API key', name it 'Imperal Live Token', and copy the key (starts with xkeysib-)."),
        ui.Text("3. Paste the API key into the form and submit."),
    ])
