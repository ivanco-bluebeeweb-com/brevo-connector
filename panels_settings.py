"""Brevo connection settings panel."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

@ext.panel("brevo_settings", slot="center")
async def brevo_settings(ctx, **kwargs) -> object:
    connections = await h._load(ctx)
    children: list[ui.UINode] = [ui.Text("Brevo — App settings", variant="heading"), ui.Divider()]
    if not connections:
        children.append(ui.Text("No Brevo accounts connected yet.", variant="caption"))
    for item in connections:
        children.extend([ui.Text(item.get("label") or "Brevo account", variant="body"), ui.Text(item.get("email", ""), variant="caption"), ui.Button("Disconnect", variant="danger", size="sm", on_click=ui.Call("disconnect_brevo", {"connection_id": item.get("id", "")})), ui.Divider()])
    return ui.Stack(direction="v", gap=2, children=children)
