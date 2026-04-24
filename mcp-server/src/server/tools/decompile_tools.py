"""
Recaf MCP Server - Decompiler Tools

Recaf 4 ships with multiple decompilers (CFR, Vineflower, Procyon). These
tools let a caller list what is available, switch the active one, and
decompile a single class with an explicit backend.
"""

from src.server.config import get_from_recaf, post_to_recaf


async def list_decompilers() -> dict:
    """
    Return the decompilers registered in Recaf's DecompilerManager, each
    with its id, display name, version, and whether it is the active one.

    MCP Tool: list_decompilers
    """
    return await get_from_recaf("decompilers")


async def set_active_decompiler(name: str) -> dict:
    """
    Set the workspace-wide default decompiler.

    Args:
        name: decompiler id as returned by list_decompilers ("cfr",
              "vineflower", "procyon")

    MCP Tool: set_active_decompiler
    """
    return await post_to_recaf("decompilers/active", {"name": name})


async def decompile_class_with(class_name: str, decompiler: str) -> dict:
    """
    One-shot decompile: run a specific decompiler against a class without
    changing the workspace default. Useful for comparing outputs.

    MCP Tool: decompile_class_with
    """
    return await get_from_recaf(
        "decompile",
        {"class_name": class_name, "decompiler": decompiler},
    )
