"""
Recaf MCP Server - Pagination Utilities

Reusable pagination framework for large Recaf datasets (class lists, search
results, references). Mirrors the jadx-mcp-server design so tool modules can
share a single standardized response shape.
"""

import json
import logging
from typing import Dict, List, Any, Union, Callable

logger = logging.getLogger("recaf-mcp-server.pagination")
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
logger.setLevel(logging.ERROR)
logger.propagate = False


class PaginationUtils:
    """
    Shared pagination helper for all Recaf MCP tools.

    Issues offset/limit query parameters to the Recaf plugin and wraps the
    response in a standard envelope so clients can iterate consistently.
    """

    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 10000
    MAX_OFFSET = 1000000

    @staticmethod
    def validate_pagination_params(offset: int, count: int) -> tuple[int, int]:
        """Clamp offset/count into safe bounds."""
        offset = max(0, min(offset, PaginationUtils.MAX_OFFSET))
        count = max(0, min(count, PaginationUtils.MAX_PAGE_SIZE))
        return offset, count

    @staticmethod
    async def get_paginated_data(
        endpoint: str,
        offset: int = 0,
        count: int = 0,
        additional_params: dict = None,
        data_extractor: Callable[[Any], List[Any]] = None,
        item_transformer: Callable[[Any], Any] = None,
        fetch_function: Callable = None
    ) -> Union[Dict[str, Any], str]:
        """
        Generic pagination handler for Recaf plugin endpoints.

        Response envelope:
            {
                "type": "paginated-list",
                "items": [...],
                "pagination": {
                    "total": int, "offset": int, "limit": int,
                    "count": int, "has_more": bool
                }
            }
        """
        offset, count = PaginationUtils.validate_pagination_params(offset, count)

        params = {"offset": offset}
        if count > 0:
            params["limit"] = count
        if additional_params:
            params.update(additional_params)

        try:
            if fetch_function is None:
                raise ValueError("fetch_function must be provided")

            response = await fetch_function(endpoint, params)
            if not isinstance(response, dict):
                return {"error": f"Unexpected response type from {endpoint}: {type(response).__name__}"}
            if response.get("error"):
                return response

            try:
                if data_extractor:
                    items = data_extractor(response)
                else:
                    items = (response.get("classes") or
                             response.get("methods") or
                             response.get("fields") or
                             response.get("items", []))

                if item_transformer and items:
                    items = [item_transformer(item) for item in items]

                return PaginationUtils._build_standardized_response(response, items)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Recaf: {e}")
                return {"error": f"Invalid JSON response from Recaf server: {str(e)}"}

        except Exception as e:
            logger.error(f"Error in paginated request to {endpoint}: {e}")
            return {"error": f"Failed to fetch data from {endpoint}: {str(e)}"}

    @staticmethod
    def _build_standardized_response(parsed_response: dict, items: List[Any]) -> dict:
        pagination_info = parsed_response.get("pagination", {})

        result = {
            "type": parsed_response.get("type", "paginated-list"),
            "items": items,
            "pagination": {
                "total": pagination_info.get("total", len(items)),
                "offset": pagination_info.get("offset", 0),
                "limit": pagination_info.get("limit", 0),
                "count": pagination_info.get("count", len(items)),
                "has_more": pagination_info.get("has_more", False)
            }
        }

        if "next_offset" in pagination_info:
            result["pagination"]["next_offset"] = pagination_info["next_offset"]
        if "prev_offset" in pagination_info:
            result["pagination"]["prev_offset"] = pagination_info["prev_offset"]
        if "current_page" in pagination_info:
            result["pagination"]["current_page"] = pagination_info["current_page"]
            result["pagination"]["total_pages"] = pagination_info.get("total_pages", 1)
            result["pagination"]["page_size"] = pagination_info.get("page_size", 0)

        return result

    @staticmethod
    def create_page_based_tool(base_func: Callable) -> Callable:
        """Decorator: convert an offset-based tool into a page-based one."""
        async def page_wrapper(page: int = 1, page_size: int = PaginationUtils.DEFAULT_PAGE_SIZE, **kwargs) -> dict:
            page = max(1, page)
            page_size = max(1, min(page_size, PaginationUtils.MAX_PAGE_SIZE))
            offset = (page - 1) * page_size
            return await base_func(offset=offset, count=page_size, **kwargs)

        return page_wrapper
