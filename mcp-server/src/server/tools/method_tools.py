"""
Recaf MCP Server - Method Analysis Tools

Inspect individual methods: decompiled body, raw bytecode, metadata. Methods
are identified by (class_name, method_name, descriptor). Descriptor is
optional when the name is unambiguous; if multiple methods share the name,
the plugin returns a disambiguation list.
"""

from src.server.config import get_from_recaf


async def get_method_by_name(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """
    Decompiled source of a single method.

    Args:
        class_name: fully qualified owner class
        method_name: method simple name (e.g. "toString", "<init>")
        descriptor: optional JVM descriptor (e.g. "(Ljava/lang/String;)V")
                    to disambiguate overloads

    MCP Tool: get_method_by_name
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await get_from_recaf("method-by-name", params)


async def get_method_bytecode(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """
    Disassembled bytecode for a single method (instructions + locals + try/catch).

    MCP Tool: get_method_bytecode
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await get_from_recaf("method-bytecode", params)


async def get_method_info(class_name: str, method_name: str, descriptor: str = "") -> dict:
    """
    Metadata for a method: access flags, return type, parameter types,
    thrown exceptions, local variable table, line numbers, annotations,
    max stack / max locals.

    MCP Tool: get_method_info
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await get_from_recaf("method-info", params)
