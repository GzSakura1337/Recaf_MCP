"""
Recaf MCP Server - Workspace Tools

Operations over the Recaf 4.0.0 Workspace: the active primary resource
(the JAR/class being analyzed), supporting resources (libraries on the
classpath), and the currently focused class/selection in the UI.
"""

from src.server.config import get_from_recaf, post_to_recaf


async def get_workspace_info() -> dict:
    """
    Return metadata about the currently loaded workspace.

    Contents: primary resource path, supporting resource paths, resource type
    (jar/war/class/directory), counts of classes and files, and whether the
    workspace has been modified since load.

    MCP Tool: get_workspace_info
    """
    return await get_from_recaf("workspace/info")


async def open_workspace(path: str) -> dict:
    """
    Load a file into Recaf as the primary workspace resource.

    Args:
        path: Absolute path to a .jar / .war / .class / .zip / directory on
              the machine running Recaf. The plugin resolves the file on its
              own filesystem (not on the MCP host).

    MCP Tool: open_workspace
    """
    return await post_to_recaf("workspace/open", {"path": path})


async def close_workspace() -> dict:
    """
    Close the current workspace without exporting.

    MCP Tool: close_workspace
    """
    return await post_to_recaf("workspace/close", {})


async def add_supporting_resource(path: str) -> dict:
    """
    Attach a supporting resource (library JAR) to the current workspace so
    that inheritance/xrefs analysis resolves symbols from it.

    MCP Tool: add_supporting_resource
    """
    return await post_to_recaf("workspace/add-supporting", {"path": path})


async def list_supporting_resources() -> dict:
    """List paths of all supporting resources attached to the workspace."""
    return await get_from_recaf("workspace/supporting")


async def fetch_current_class() -> dict:
    """
    Fetch the class currently focused in the Recaf UI (active editor tab).

    Returns class name plus the decompiled Java source for it (using the
    active decompiler configured in Recaf).

    MCP Tool: fetch_current_class
    """
    return await get_from_recaf("current-class")


async def get_selected_text() -> dict:
    """
    Return the text currently selected in the active Recaf editor.

    Useful for focused analysis: ask the model to explain a highlighted
    method body or operand without dumping the whole class.

    MCP Tool: get_selected_text
    """
    return await get_from_recaf("selected-text")
