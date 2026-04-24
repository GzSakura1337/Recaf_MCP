"""
Recaf MCP Server - Inheritance Tools

Query Recaf's inheritance graph: supertypes, subtypes, and implementors.
All lookups include both workspace classes and classes from supporting
resources (libraries + JDK) when Recaf has them indexed.
"""

from src.server.config import get_from_recaf
from src.PaginationUtils import PaginationUtils


async def get_superclasses(class_name: str) -> dict:
    """
    Walk from the class up to java.lang.Object. Returns an ordered list
    starting with the direct superclass.

    MCP Tool: get_superclasses
    """
    return await get_from_recaf("inheritance/superclasses", {"class_name": class_name})


async def get_interfaces(class_name: str) -> dict:
    """
    All interfaces implemented by the class, including those inherited
    transitively from supertypes.

    MCP Tool: get_interfaces
    """
    return await get_from_recaf("inheritance/interfaces", {"class_name": class_name})


async def get_direct_subclasses(class_name: str, offset: int = 0, count: int = 50) -> dict:
    """
    Classes that directly extend `class_name` (one level down).

    MCP Tool: get_direct_subclasses
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="inheritance/direct-subclasses",
        offset=offset,
        count=count,
        additional_params={"class_name": class_name},
        data_extractor=lambda parsed: parsed.get("classes", []),
        fetch_function=get_from_recaf,
    )


async def get_all_subclasses(class_name: str, offset: int = 0, count: int = 200) -> dict:
    """
    All transitive descendants of `class_name`.

    MCP Tool: get_all_subclasses
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="inheritance/all-subclasses",
        offset=offset,
        count=count,
        additional_params={"class_name": class_name},
        data_extractor=lambda parsed: parsed.get("classes", []),
        fetch_function=get_from_recaf,
    )


async def get_implementors(interface_name: str, offset: int = 0, count: int = 200) -> dict:
    """
    Classes that implement the given interface (directly or transitively).

    MCP Tool: get_implementors
    """
    return await PaginationUtils.get_paginated_data(
        endpoint="inheritance/implementors",
        offset=offset,
        count=count,
        additional_params={"interface_name": interface_name},
        data_extractor=lambda parsed: parsed.get("classes", []),
        fetch_function=get_from_recaf,
    )
