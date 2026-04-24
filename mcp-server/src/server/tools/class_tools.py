"""
Recaf MCP Server - Class Analysis Tools

Enumerate and inspect classes loaded in the Recaf workspace. Class names use
JVM internal form with '.' separators (e.g. "com.example.Foo$Bar"); the
plugin internally converts to slash form when talking to ASM.
"""

from src.server.config import get_from_recaf
from src.PaginationUtils import PaginationUtils


async def get_all_classes(offset: int = 0, count: int = 0) -> dict:
    """
    Paginated listing of every class in the primary resource.

    Args:
        offset: starting index (default 0)
        count: max items (0 = plugin-defined default)

    MCP Tool: get_all_classes
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="all-classes",
        offset=offset,
        count=count,
        data_extractor=lambda parsed: parsed.get("classes", []),
        fetch_function=get_from_recaf
    )


async def get_class_info(class_name: str) -> dict:
    """
    Basic metadata for a class: access flags, superclass, interfaces, outer
    class, source file attribute, major/minor version, annotation list,
    signature (generics), counts of methods/fields/inner classes.

    MCP Tool: get_class_info
    """
    return await get_from_recaf("class-info", {"class_name": class_name})


async def get_class_source(class_name: str, decompiler: str = "") -> dict:
    """
    Decompile a class to Java source.

    Args:
        class_name: fully qualified name (dot-separated)
        decompiler: optional decompiler id ("cfr", "vineflower", "procyon").
                    Empty string uses the workspace-level active decompiler.

    MCP Tool: get_class_source
    """
    params = {"class_name": class_name}
    if decompiler:
        params["decompiler"] = decompiler
    return await get_from_recaf("class-source", params)


async def get_bytecode_of_class(class_name: str) -> dict:
    """
    Disassembled bytecode view of a class — Recaf's equivalent of JADX smali.
    Uses the assembler printer so the output can be round-tripped via the
    assemble endpoint.

    MCP Tool: get_bytecode_of_class
    """
    return await get_from_recaf("bytecode-of-class", {"class_name": class_name})


async def get_methods_of_class(class_name: str) -> dict:
    """List every method on a class with name + JVM descriptor + access flags."""
    return await get_from_recaf("methods-of-class", {"class_name": class_name})


async def get_fields_of_class(class_name: str) -> dict:
    """List every field on a class with name + JVM descriptor + access flags."""
    return await get_from_recaf("fields-of-class", {"class_name": class_name})


async def get_inner_classes(class_name: str) -> dict:
    """List inner/nested class names declared within the given class."""
    return await get_from_recaf("inner-classes", {"class_name": class_name})


async def get_annotations_of_class(class_name: str) -> dict:
    """Runtime-visible and invisible annotations attached to the class."""
    return await get_from_recaf("annotations-of-class", {"class_name": class_name})


async def get_raw_class_bytes(class_name: str) -> dict:
    """
    Base64-encoded raw class file bytes.

    Useful when a caller wants to feed the class into an external tool (ASM,
    bcel, etc.) rather than rely on Recaf's decompiler or disassembler.

    MCP Tool: get_raw_class_bytes
    """
    return await get_from_recaf("class-bytes", {"class_name": class_name})
