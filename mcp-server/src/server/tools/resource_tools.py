"""
Recaf MCP Server - File Resource Tools

Access non-class files bundled in the primary resource (manifest entries,
META-INF/*, embedded resources). Binary files are returned base64-encoded;
text files are returned as-is with an explicit encoding field.
"""

from src.server.config import get_from_recaf
from src.PaginationUtils import PaginationUtils


async def get_all_file_names(offset: int = 0, count: int = 0) -> dict:
    """
    Paginated list of every non-class file path in the primary resource.

    MCP Tool: get_all_file_names
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="files/list",
        offset=offset,
        count=count,
        data_extractor=lambda parsed: parsed.get("files", []),
        fetch_function=get_from_recaf,
    )


async def get_file_content(file_path: str) -> dict:
    """
    Retrieve the content of a file inside the primary resource.

    Args:
        file_path: archive-relative path (e.g. "META-INF/MANIFEST.MF")

    Returns a dict with `content` (text or base64), `encoding` ("utf-8" or
    "base64"), `size`, and `mime` when the plugin can detect it.

    MCP Tool: get_file_content
    """
    return await get_from_recaf("files/content", {"path": file_path})


async def get_manifest() -> dict:
    """
    Shortcut for the JAR's META-INF/MANIFEST.MF parsed into main attributes
    and per-entry attributes.

    MCP Tool: get_manifest
    """
    return await get_from_recaf("files/manifest")


async def get_strings_from_resources(offset: int = 0, count: int = 0) -> dict:
    """
    Extract printable strings from non-class binary resources (useful for
    finding embedded config keys, URLs, native-library symbols).

    MCP Tool: get_strings_from_resources
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="files/strings",
        offset=offset,
        count=count,
        data_extractor=lambda parsed: parsed.get("strings", []),
        fetch_function=get_from_recaf,
    )
