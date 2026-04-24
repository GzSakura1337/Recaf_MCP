"""
Recaf MCP Server - Export Tools

Write the (possibly modified) workspace back to disk. Exports run through
Recaf's own ResourceExporter so packaging rules (manifest, module-info,
multi-release entries) are preserved.
"""

from src.server.config import get_from_recaf, post_to_recaf


async def export_workspace(output_path: str, include_supporting: bool = False) -> dict:
    """
    Write the primary resource to `output_path`. The file format matches the
    original resource (jar → jar, class → class, directory → directory).

    Args:
        output_path: absolute path on the machine running Recaf
        include_supporting: if True, supporting resources are merged into
                            the output (e.g. shaded-jar style). Default
                            False, which writes only the primary resource.

    MCP Tool: export_workspace
    """
    return await post_to_recaf("export/workspace", {
        "output_path": output_path,
        "include_supporting": include_supporting,
    })


async def get_modified_classes() -> dict:
    """
    List classes that have been modified relative to their original bytes
    (renames, assembled patches, decompile-then-recompile edits).

    MCP Tool: get_modified_classes
    """
    return await get_from_recaf("export/modified-classes")


async def revert_class(class_name: str) -> dict:
    """
    Discard in-memory modifications to a single class and restore it from
    the originally loaded bytes.

    MCP Tool: revert_class
    """
    return await post_to_recaf("export/revert-class", {"class_name": class_name})
