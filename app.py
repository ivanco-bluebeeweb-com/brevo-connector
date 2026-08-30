"""Brevo Connector extension declaration."""
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "brevo-connector", version="0.1.0", display_name="Brevo", icon="icon.svg",
    capabilities=["brevo:read", "brevo:write"],
    description="Connect Brevo with an API key to manage contacts, lists, campaigns, and transactional email.",
)
chat = ChatExtension(ext)


@ext.health_check
async def health_check(ctx) -> dict:
    """Fast configuration health; no third-party call -- just confirms at
    least one account connection is stored, same shape as Buildium's/Cin7
    Core's health_check."""
    import json as _json
    raw = await ctx.secrets.get("brevo_connections")
    try:
        count = len(_json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": (
            f"{count} Brevo account(s) connected." if count
            else "Not connected yet -- run connect_brevo."
        ),
    }
