"""
Recaf MCP Server - Cross-Reference Tools

Find callers/callees and usage sites of classes, methods, and fields.
"""

from src.server.config import get_from_recaf
from src.PaginationUtils import PaginationUtils


async def get_xrefs_to_class(class_name: str, offset: int = 0, count: int = 20) -> dict:
    """
    Locations that reference `class_name` (type uses, `new` sites, method
    signatures, field types, casts, annotations).

    MCP Tool: get_xrefs_to_class
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="xrefs-to-class",
        offset=offset,
        count=count,
        additional_params={"class_name": class_name},
        data_extractor=lambda parsed: parsed.get("references", []),
        fetch_function=get_from_recaf,
    )


async def get_xrefs_to_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """
    Call sites that invoke the method. Includes INVOKEVIRTUAL / STATIC /
    SPECIAL / INTERFACE / DYNAMIC. Overrides are NOT included by default —
    use get_overrides_of_method to walk the override tree.

    MCP Tool: get_xrefs_to_method
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await PaginationUtils.get_paginated_data(
        endpoint="xrefs-to-method",
        offset=offset,
        count=count,
        additional_params=params,
        data_extractor=lambda parsed: parsed.get("references", []),
        fetch_function=get_from_recaf,
    )


async def get_xrefs_to_field(
    class_name: str,
    field_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """
    Locations that read or write the field (GETFIELD / PUTFIELD /
    GETSTATIC / PUTSTATIC).

    MCP Tool: get_xrefs_to_field
    """
    params = {"class_name": class_name, "field_name": field_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await PaginationUtils.get_paginated_data(
        endpoint="xrefs-to-field",
        offset=offset,
        count=count,
        additional_params=params,
        data_extractor=lambda parsed: parsed.get("references", []),
        fetch_function=get_from_recaf,
    )


async def get_callers_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 20,
) -> dict:
    """
    Alias for get_xrefs_to_method, exposed separately for clarity when
    building call-graph workflows.

    MCP Tool: get_callers_of_method
    """
    return await get_xrefs_to_method(class_name, method_name, descriptor, offset, count)


async def get_callees_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    Methods invoked by the body of the given method (forward call edges).

    MCP Tool: get_callees_of_method
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await PaginationUtils.get_paginated_data(
        endpoint="callees-of-method",
        offset=offset,
        count=count,
        additional_params=params,
        data_extractor=lambda parsed: parsed.get("callees", []),
        fetch_function=get_from_recaf,
    )


async def get_overrides_of_method(
    class_name: str,
    method_name: str,
    descriptor: str = "",
    offset: int = 0,
    count: int = 50,
) -> dict:
    """
    All methods that override or implement the given virtual/interface method
    (walks the inheritance graph in both directions).

    MCP Tool: get_overrides_of_method
    """
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await PaginationUtils.get_paginated_data(
        endpoint="overrides-of-method",
        offset=offset,
        count=count,
        additional_params=params,
        data_extractor=lambda parsed: parsed.get("overrides", []),
        fetch_function=get_from_recaf,
    )
