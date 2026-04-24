#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [ "fastmcp>=3.0.2", "httpx" ]
# ///

"""
Recaf MCP Server — reverse engineering MCP for Recaf 4.0.0.

Mirrors the jadx-mcp-server architecture: this Python process hosts the
MCP tools and forwards each call as HTTP to the Recaf plugin running
inside the Recaf JavaFX process.

Default ports:
    Recaf plugin HTTP ..... 8750
    Recaf MCP (streamable). 8751
"""

import argparse
import logging
import sys
from fastmcp import FastMCP
from src.banner import recaf_mcp_server_banner
from src.server import config, tools

mcp = FastMCP("Recaf MCP Plugin Reverse Engineering Server")

# Bootstrap logger — always writes to stderr to keep stdout clean for stdio transport
logger = logging.getLogger("recaf-mcp-server.bootstrap")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


# Import tool modules so FastMCP decorators below can forward into them.
# The bare `import` form registers the submodule as an attribute of the
# `tools` package, matching the jadx-mcp-server style.
from src.server.tools import (
    workspace_tools,
    class_tools,
    method_tools,
    search_tools,
    xrefs_tools,
    refactor_tools,
    decompile_tools,
    inheritance_tools,
    resource_tools,
    export_tools,
)


# =============================================================================
# Workspace
# =============================================================================

@mcp.tool()
async def get_workspace_info() -> dict:
    """Return metadata about the currently loaded Recaf workspace."""
    return await tools.workspace_tools.get_workspace_info()


@mcp.tool()
async def open_workspace(path: str) -> dict:
    """Load a JAR/class/directory into Recaf as the primary workspace resource."""
    return await tools.workspace_tools.open_workspace(path)


@mcp.tool()
async def close_workspace() -> dict:
    """Close the current workspace without exporting."""
    return await tools.workspace_tools.close_workspace()


@mcp.tool()
async def add_supporting_resource(path: str) -> dict:
    """Attach a supporting library JAR to the workspace for inheritance/xref resolution."""
    return await tools.workspace_tools.add_supporting_resource(path)


@mcp.tool()
async def list_supporting_resources() -> dict:
    """List all supporting resources (library JARs) attached to the workspace."""
    return await tools.workspace_tools.list_supporting_resources()


@mcp.tool()
async def fetch_current_class() -> dict:
    """Fetch the class currently focused in the Recaf UI (active editor tab)."""
    return await tools.workspace_tools.fetch_current_class()


@mcp.tool()
async def get_selected_text() -> dict:
    """Return the text currently selected in the active Recaf editor."""
    return await tools.workspace_tools.get_selected_text()


# =============================================================================
# Classes
# =============================================================================

@mcp.tool()
async def get_all_classes(offset: int = 0, count: int = 0) -> dict:
    """Paginated listing of every class in the primary resource."""
    return await tools.class_tools.get_all_classes(offset, count)


@mcp.tool()
async def get_class_info(class_name: str) -> dict:
    """Basic metadata for a class: access flags, supertypes, counts, annotations."""
    return await tools.class_tools.get_class_info(class_name)


@mcp.tool()
async def get_class_source(class_name: str, decompiler: str = "") -> dict:
    """Decompile a class to Java source. Optional decompiler id overrides the default."""
    return await tools.class_tools.get_class_source(class_name, decompiler)


@mcp.tool()
async def get_bytecode_of_class(class_name: str) -> dict:
    """Disassembled bytecode view of a class (Recaf's equivalent of smali)."""
    return await tools.class_tools.get_bytecode_of_class(class_name)


@mcp.tool()
async def get_methods_of_class(class_name: str) -> dict:
    """List every method on a class with name, JVM descriptor, and access flags."""
    return await tools.class_tools.get_methods_of_class(class_name)


@mcp.tool()
async def get_fields_of_class(class_name: str) -> dict:
    """List every field on a class with name, JVM descriptor, and access flags."""
    return await tools.class_tools.get_fields_of_class(class_name)


@mcp.tool()
async def get_inner_classes(class_name: str) -> dict:
    """List inner/nested class names declared within the given class."""
    return await tools.class_tools.get_inner_classes(class_name)


@mcp.tool()
async def get_annotations_of_class(class_name: str) -> dict:
    """All annotations (visible and invisible) attached to the class."""
    return await tools.class_tools.get_annotations_of_class(class_name)


@mcp.tool()
async def get_raw_class_bytes(class_name: str) -> dict:
    """Base64-encoded raw class file bytes for external tooling."""
    return await tools.class_tools.get_raw_class_bytes(class_name)


# =============================================================================
# Methods
# =============================================================================

@mcp.tool()
async def get_method_by_name(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """Decompiled source of a single method (optionally disambiguated by descriptor)."""
    return await tools.method_tools.get_method_by_name(class_name, method_name, descriptor)


@mcp.tool()
async def get_method_bytecode(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """Disassembled bytecode for a single method (instructions, locals, try/catch)."""
    return await tools.method_tools.get_method_bytecode(class_name, method_name, descriptor)


@mcp.tool()
async def get_method_info(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """Method metadata: access, signature, exceptions, locals, line numbers."""
    return await tools.method_tools.get_method_info(class_name, method_name, descriptor)


# =============================================================================
# Search
# =============================================================================

@mcp.tool()
async def search_classes_by_name(
    pattern: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """Find classes whose fully qualified name matches the given pattern."""
    return await tools.search_tools.search_classes_by_name(
        pattern, use_regex, case_sensitive, offset, count
    )


@mcp.tool()
async def search_members_by_name(
    pattern: str,
    kind: str = "any",
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """Find methods and/or fields by name. `kind` is "method", "field", or "any"."""
    return await tools.search_tools.search_members_by_name(
        pattern, kind, use_regex, case_sensitive, offset, count
    )


@mcp.tool()
async def search_strings(
    pattern: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """Search string constants in code (LDC / constant pool)."""
    return await tools.search_tools.search_strings(
        pattern, use_regex, case_sensitive, offset, count
    )


@mcp.tool()
async def search_numbers(value: str, offset: int = 0, count: int = 50) -> dict:
    """Search numeric constants (int/long/float/double) appearing in bytecode."""
    return await tools.search_tools.search_numbers(value, offset, count)


@mcp.tool()
async def search_instructions(
    opcode: str = "",
    operand: str = "",
    class_filter: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """Bytecode-level search by opcode mnemonic and/or operand substring."""
    return await tools.search_tools.search_instructions(
        opcode, operand, class_filter, offset, count
    )


# =============================================================================
# Cross-references
# =============================================================================

@mcp.tool()
async def get_xrefs_to_class(class_name: str, offset: int = 0, count: int = 20) -> dict:
    """Find every location that references a class."""
    return await tools.xrefs_tools.get_xrefs_to_class(class_name, offset, count)


@mcp.tool()
async def get_xrefs_to_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """Find every call site that invokes a method."""
    return await tools.xrefs_tools.get_xrefs_to_method(
        class_name, method_name, descriptor, offset, count
    )


@mcp.tool()
async def get_xrefs_to_field(
    class_name: str,
    field_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """Find every read/write site for a field."""
    return await tools.xrefs_tools.get_xrefs_to_field(
        class_name, field_name, descriptor, offset, count
    )


@mcp.tool()
async def get_callers_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """Alias for get_xrefs_to_method — call sites that invoke the method."""
    return await tools.xrefs_tools.get_callers_of_method(
        class_name, method_name, descriptor, offset, count
    )


@mcp.tool()
async def get_callees_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """Methods invoked by the body of the given method (forward call edges)."""
    return await tools.xrefs_tools.get_callees_of_method(
        class_name, method_name, descriptor, offset, count
    )


@mcp.tool()
async def get_overrides_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """All methods that override or implement the given virtual/interface method."""
    return await tools.xrefs_tools.get_overrides_of_method(
        class_name, method_name, descriptor, offset, count
    )


# =============================================================================
# Refactor
# =============================================================================

@mcp.tool()
async def rename_class(class_name: str, new_name: str) -> dict:
    """Rename a class across the entire workspace."""
    return await tools.refactor_tools.rename_class(class_name, new_name)


@mcp.tool()
async def rename_method(
    class_name: str,
    method_name: str,
    new_name: str,
    descriptor: str = "",
    cascade_overrides: bool = True,
) -> dict:
    """Rename a method. Cascades to overrides/implementations by default."""
    return await tools.refactor_tools.rename_method(
        class_name, method_name, new_name, descriptor, cascade_overrides
    )


@mcp.tool()
async def rename_field(
    class_name: str,
    field_name: str,
    new_name: str,
    descriptor: str = "",
) -> dict:
    """Rename a field and update every read/write site."""
    return await tools.refactor_tools.rename_field(
        class_name, field_name, new_name, descriptor
    )


@mcp.tool()
async def rename_package(old_package_name: str, new_package_name: str) -> dict:
    """Rename a package prefix and move every class under it."""
    return await tools.refactor_tools.rename_package(old_package_name, new_package_name)


@mcp.tool()
async def rename_local_variable(
    class_name: str,
    method_name: str,
    variable_name: str,
    new_name: str,
    descriptor: str = "",
    index: int = -1,
) -> dict:
    """Rename a local variable in a method's LocalVariableTable (cosmetic)."""
    return await tools.refactor_tools.rename_local_variable(
        class_name, method_name, variable_name, new_name, descriptor, index
    )


@mcp.tool()
async def apply_mappings(mappings_text: str, format: str = "tiny-v2") -> dict:
    """Bulk-apply a mapping file (Proguard/SRG/TSRG/Tiny v1-v2/Enigma)."""
    return await tools.refactor_tools.apply_mappings(mappings_text, format)


# =============================================================================
# Decompilers
# =============================================================================

@mcp.tool()
async def list_decompilers() -> dict:
    """List decompilers registered in Recaf's DecompilerManager."""
    return await tools.decompile_tools.list_decompilers()


@mcp.tool()
async def set_active_decompiler(name: str) -> dict:
    """Set the workspace-wide default decompiler (cfr / vineflower / procyon)."""
    return await tools.decompile_tools.set_active_decompiler(name)


@mcp.tool()
async def decompile_class_with(class_name: str, decompiler: str) -> dict:
    """One-shot decompile with an explicit decompiler; workspace default unchanged."""
    return await tools.decompile_tools.decompile_class_with(class_name, decompiler)


# =============================================================================
# Inheritance
# =============================================================================

@mcp.tool()
async def get_superclasses(class_name: str) -> dict:
    """Walk from the class up to java.lang.Object."""
    return await tools.inheritance_tools.get_superclasses(class_name)


@mcp.tool()
async def get_interfaces(class_name: str) -> dict:
    """All interfaces implemented by the class (direct + transitive)."""
    return await tools.inheritance_tools.get_interfaces(class_name)


@mcp.tool()
async def get_direct_subclasses(class_name: str, offset: int = 0, count: int = 50) -> dict:
    """Classes that directly extend the given class (one level down)."""
    return await tools.inheritance_tools.get_direct_subclasses(class_name, offset, count)


@mcp.tool()
async def get_all_subclasses(class_name: str, offset: int = 0, count: int = 200) -> dict:
    """All transitive descendants of the given class."""
    return await tools.inheritance_tools.get_all_subclasses(class_name, offset, count)


@mcp.tool()
async def get_implementors(interface_name: str, offset: int = 0, count: int = 200) -> dict:
    """All classes that implement the given interface."""
    return await tools.inheritance_tools.get_implementors(interface_name, offset, count)


# =============================================================================
# File resources (non-class files in the jar)
# =============================================================================

@mcp.tool()
async def get_all_file_names(offset: int = 0, count: int = 0) -> dict:
    """Paginated list of every non-class file path in the primary resource."""
    return await tools.resource_tools.get_all_file_names(offset, count)


@mcp.tool()
async def get_file_content(file_path: str) -> dict:
    """Retrieve the content of a file inside the primary resource."""
    return await tools.resource_tools.get_file_content(file_path)


@mcp.tool()
async def get_manifest() -> dict:
    """Parsed META-INF/MANIFEST.MF (main attributes + per-entry attributes)."""
    return await tools.resource_tools.get_manifest()


@mcp.tool()
async def get_strings_from_resources(offset: int = 0, count: int = 0) -> dict:
    """Extract printable strings from non-class binary resources."""
    return await tools.resource_tools.get_strings_from_resources(offset, count)


# =============================================================================
# Export
# =============================================================================

@mcp.tool()
async def export_workspace(output_path: str, include_supporting: bool = False) -> dict:
    """Write the (possibly modified) primary resource back to disk."""
    return await tools.export_tools.export_workspace(output_path, include_supporting)


@mcp.tool()
async def get_modified_classes() -> dict:
    """List classes that have been modified relative to their original bytes."""
    return await tools.export_tools.get_modified_classes()


@mcp.tool()
async def revert_class(class_name: str) -> dict:
    """Discard in-memory modifications to a class and restore the original bytes."""
    return await tools.export_tools.revert_class(class_name)


# =============================================================================
# Entrypoint
# =============================================================================

def main():
    parser = argparse.ArgumentParser("MCP Server for Recaf")
    parser.add_argument(
        "--http",
        help="Serve MCP Server over HTTP stream.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--host",
        help="Host address to bind for --http (default: 127.0.0.1, use 0.0.0.0 for remote access). "
             "WARNING: non-localhost binds expose the server over plain HTTP with no authentication.",
        default="127.0.0.1",
        type=str,
    )
    parser.add_argument(
        "--port",
        help="Port for --http (default: 8751)",
        default=8751,
        type=int,
    )
    parser.add_argument(
        "--recaf-port",
        help="Recaf MCP plugin port (default: 8750)",
        default=8750,
        type=int,
    )
    parser.add_argument(
        "--recaf-host",
        help="Recaf MCP plugin host (default: 127.0.0.1). "
             "Security: non-localhost may expose the plugin to the network.",
        default="127.0.0.1",
        type=str,
    )
    args = parser.parse_args()

    config.set_recaf_host(args.recaf_host)
    config.set_recaf_port(args.recaf_port)

    if args.host not in ("127.0.0.1", "localhost", "::1"):
        logger.warning(
            "\n⚠️  SECURITY WARNING: Binding to non-localhost address '%s'.\n"
            "   The MCP server uses plain HTTP with NO authentication.\n"
            "   Anyone on the network can connect and use all MCP tools.\n"
            "   Only use this on trusted networks or behind a firewall.",
            args.host,
        )

    try:
        logger.info(recaf_mcp_server_banner())
    except Exception:
        logger.info(
            "[Recaf MCP Server] v0.1.0 | MCP Port: %s | Recaf Host: %s | Recaf Port: %s",
            args.port,
            args.recaf_host,
            args.recaf_port,
        )

    logger.info("Testing Recaf MCP Plugin connectivity...")
    result = config.health_ping()
    logger.info("Health check result: %s", result)

    if args.http:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
