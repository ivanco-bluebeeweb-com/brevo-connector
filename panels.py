"""Brevo sidebar UI following the shared UI interface standard."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings() -> ui.UINode:
    return ui.Button("App settings", variant="secondary", size="sm", full_width=True, icon="settings", on_click=ui.Call("__panel__brevo_settings"))

@ext.panel("home", slot="left")
async def home(ctx, **kwargs) -> object:
    connections = await h._load(ctx)
    form = ui.Form(
        submit_label="Connect Brevo", action=ui.Call("connect_brevo"),
        children=[ui.Stack(direction="v", gap=2, children=[
            ui.Stack(direction="v", gap=1, children=[ui.Text("Account label", variant="label"), ui.Input(param_name="label", placeholder="e.g. Marketing workspace")]),
            ui.Stack(direction="v", gap=1, children=[ui.Text("API key", variant="label"), ui.Input(param_name="api_key", placeholder="Paste the key from SMTP & API > API Keys")]),
        ])],
    )
    children: list[ui.UINode] = [ui.Text("Brevo", variant="heading")]
    if connections:
        children.extend([ui.Text("Connected accounts", variant="label"), *[ui.Text(x.get("label") or "Brevo account", variant="body") for x in connections]])
    else:
        children.extend([ui.Text("Connect an account", variant="label"), form])
    children.extend([ui.Button("How do I set this up?", variant="secondary", size="sm", full_width=True, on_click=ui.OpenModal("brevo_setup")), _settings()])
    return ui.Stack(direction="v", gap=3, children=children)

@ext.panel("brevo_setup", slot="overlay")
async def brevo_setup(ctx, **kwargs) -> object:
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text("Connect Brevo", variant="heading"),
        ui.Text("In Brevo, open SMTP & API → API Keys, create an API key with the access you need, then paste it here. The key is verified before it is saved.", variant="body"),
    ])
