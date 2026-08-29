"""Brevo Connector extension declaration."""
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "brevo-connector", version="0.1.0", display_name="Brevo", icon="icon.svg",
    capabilities=["brevo:read", "brevo:write"],
    description="Connect Brevo with an API key to manage contacts, lists, campaigns, and transactional email.",
)
chat = ChatExtension(ext)
