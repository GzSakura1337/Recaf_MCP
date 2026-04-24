"""
Recaf MCP Server - Refactor Tools

Rename operations go through Recaf's mapping system so every reference in
the workspace (including bytecode operands) is updated atomically. All
mutation endpoints use POST.
"""

from src.server.config import post_to_recaf


async def rename_class(class_name: str, new_name: str) -> dict:
    """
    Rename a class across the entire workspace (updates every descriptor
    and type use via the mapping applier).

    Args:
        class_name: current fully qualified name (dot-separated)
        new_name: new fully qualified name (dot-separated)

    MCP Tool: rename_class
    """
    return await post_to_recaf("rename/class", {
        "class_name": class_name,
        "new_name": new_name,
    })


async def rename_method(
    class_name: str,
    method_name: str,
    new_name: str,
    descriptor: str = "",
    cascade_overrides: bool = True,
) -> dict:
    """
    Rename a method. By default cascades to every override / implementation
    in the inheritance graph so runtime dispatch still resolves.

    Args:
        class_name: owner class
        method_name: current method name
        new_name: replacement name
        descriptor: JVM descriptor; required when the owner has overloads
        cascade_overrides: also rename overriding methods (default True)

    MCP Tool: rename_method
    """
    return await post_to_recaf("rename/method", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "new_name": new_name,
        "cascade_overrides": cascade_overrides,
    })


async def rename_field(
    class_name: str,
    field_name: str,
    new_name: str,
    descriptor: str = "",
) -> dict:
    """
    Rename a field and update every read/write site.

    Args:
        descriptor: optional JVM type descriptor for disambiguation
                    (fields can share names across hierarchies)

    MCP Tool: rename_field
    """
    return await post_to_recaf("rename/field", {
        "class_name": class_name,
        "field_name": field_name,
        "descriptor": descriptor,
        "new_name": new_name,
    })


async def rename_package(old_package_name: str, new_package_name: str) -> dict:
    """
    Rename a package prefix. All classes under `old_package_name` are moved
    to `new_package_name`, updating every descriptor in the workspace.

    MCP Tool: rename_package
    """
    return await post_to_recaf("rename/package", {
        "old_package_name": old_package_name,
        "new_package_name": new_package_name,
    })


async def rename_local_variable(
    class_name: str,
    method_name: str,
    variable_name: str,
    new_name: str,
    descriptor: str = "",
    index: int = -1,
) -> dict:
    """
    Rename a local variable entry in a method's LocalVariableTable. This is
    cosmetic only (variables are resolved by index at runtime) and affects
    the decompiled output + JASM view.

    Args:
        index: optional local variable table index for disambiguation when
               multiple entries share the same name. -1 = rename all matches.

    MCP Tool: rename_local_variable
    """
    return await post_to_recaf("rename/local-variable", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "variable_name": variable_name,
        "new_name": new_name,
        "index": index,
    })


async def apply_mappings(mappings_text: str, format: str = "tiny-v2") -> dict:
    """
    Bulk-apply a mapping file (Proguard, SRG, TSRG, Tiny v1/v2, Enigma).

    Args:
        mappings_text: raw mappings file content
        format: one of "proguard", "srg", "tsrg", "tsrg2", "tiny-v1",
                "tiny-v2", "enigma"

    MCP Tool: apply_mappings
    """
    return await post_to_recaf("rename/apply-mappings", {
        "mappings": mappings_text,
        "format": format,
    })
