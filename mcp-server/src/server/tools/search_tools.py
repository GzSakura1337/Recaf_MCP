"""
Recaf MCP Server - Search Tools

Wraps Recaf's search service. Recaf separates searches by what is being
matched (class name, member name, string constant, numeric constant,
bytecode instruction) — this module exposes each as its own MCP tool.
"""

from src.server.config import get_from_recaf
from src.PaginationUtils import PaginationUtils


async def search_classes_by_name(
    pattern: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Find classes whose fully-qualified name matches `pattern`.

    Args:
        pattern: text or regex
        use_regex: treat `pattern` as a Java regex
        case_sensitive: case-sensitive matching (default True)

    MCP Tool: search_classes_by_name
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="search/classes",
        offset=offset,
        count=count,
        additional_params={
            "pattern": pattern,
            "regex": str(use_regex).lower(),
            "case_sensitive": str(case_sensitive).lower(),
        },
        data_extractor=lambda parsed: parsed.get("classes", []),
        fetch_function=get_from_recaf,
    )


async def search_members_by_name(
    pattern: str,
    kind: str = "any",
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Find methods and/or fields whose simple name matches `pattern`.

    Args:
        pattern: text or regex
        kind: "method", "field", or "any" (default)
        use_regex / case_sensitive: as in search_classes_by_name

    MCP Tool: search_members_by_name
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="search/members",
        offset=offset,
        count=count,
        additional_params={
            "pattern": pattern,
            "kind": kind,
            "regex": str(use_regex).lower(),
            "case_sensitive": str(case_sensitive).lower(),
        },
        data_extractor=lambda parsed: parsed.get("members", []),
        fetch_function=get_from_recaf,
    )


async def search_strings(
    pattern: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Search for string constants in code (LDC / constant pool) matching
    `pattern`. Returns each hit with owning class, method, and bytecode
    offset where the literal appears.

    MCP Tool: search_strings
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="search/strings",
        offset=offset,
        count=count,
        additional_params={
            "pattern": pattern,
            "regex": str(use_regex).lower(),
            "case_sensitive": str(case_sensitive).lower(),
        },
        data_extractor=lambda parsed: parsed.get("hits", []),
        fetch_function=get_from_recaf,
    )


async def search_numbers(
    value: str,
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Search for numeric constants (int / long / float / double) appearing in
    code. `value` is passed as a string so callers can express values that
    overflow JSON-safe ints (e.g. long literals).

    MCP Tool: search_numbers
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="search/numbers",
        offset=offset,
        count=count,
        additional_params={"value": value},
        data_extractor=lambda parsed: parsed.get("hits", []),
        fetch_function=get_from_recaf,
    )


async def search_instructions(
    opcode: str = "",
    operand: str = "",
    class_filter: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Bytecode-level search for instructions matching an opcode and/or operand.

    Args:
        opcode: mnemonic (e.g. "invokestatic", "ldc", "getfield"). Empty =
                any opcode.
        operand: substring to match against the pretty-printed operand.
        class_filter: restrict the search to classes under a given package
                      prefix (empty = search whole workspace).

    MCP Tool: search_instructions
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="search/instructions",
        offset=offset,
        count=count,
        additional_params={
            "opcode": opcode,
            "operand": operand,
            "class_filter": class_filter,
        },
        data_extractor=lambda parsed: parsed.get("hits", []),
        fetch_function=get_from_recaf,
    )
