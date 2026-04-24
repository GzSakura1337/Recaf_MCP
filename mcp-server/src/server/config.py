"""
Recaf MCP Server - Configuration Module

Manages HTTP client setup and communication with the Recaf 4.0.0 plugin.
The plugin must expose a local HTTP server (default 127.0.0.1:8750) that
implements the endpoints consumed by the tool modules under src/server/tools/.
"""

import logging
import httpx
import json
import sys
from typing import Union, Dict, Any

# Default Configuration — Recaf plugin is expected on 8750 by convention
# (jadx-mcp-server uses 8650, we shift up to avoid collision when both run).
RECAF_HOST = "127.0.0.1"
RECAF_PORT = 8750
RECAF_HTTP_BASE = f"http://{RECAF_HOST}:{RECAF_PORT}"

logger = logging.getLogger("recaf-mcp-server")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)
logger.propagate = False


def _rebuild_recaf_http_base():
    global RECAF_HTTP_BASE
    RECAF_HTTP_BASE = f"http://{RECAF_HOST}:{RECAF_PORT}"


def set_recaf_host(host: str):
    """Update the Recaf plugin host and rebuild the base URL."""
    global RECAF_HOST
    RECAF_HOST = host
    _rebuild_recaf_http_base()


def set_recaf_port(port: int):
    """Update the Recaf plugin port and rebuild the base URL."""
    global RECAF_PORT
    RECAF_PORT = port
    _rebuild_recaf_http_base()


def health_ping() -> Union[str, Dict[str, Any]]:
    """Synchronous health check against the Recaf plugin."""
    try:
        with httpx.Client(trust_env=False) as client:
            resp = client.get(f"{RECAF_HTTP_BASE}/health", timeout=60)
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"error": str(e)}


async def get_from_recaf(endpoint: str, params: Dict[str, Any] = None) -> Union[str, Dict[str, Any]]:
    """
    GET against the Recaf plugin.

    JSON is parsed when possible; otherwise the raw text is returned as
    {"response": "..."}. HTTP errors surface as {"error": "..."}.
    """
    if params is None:
        params = {}
    url = f"{RECAF_HTTP_BASE}/{endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(trust_env=False) as client:
            resp = await client.get(url, params=params, timeout=60)
            resp.raise_for_status()
            try:
                return resp.json()
            except json.JSONDecodeError:
                return {"response": resp.text}

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


async def post_to_recaf(endpoint: str, payload: Dict[str, Any] = None) -> Union[str, Dict[str, Any]]:
    """
    POST JSON to the Recaf plugin.

    Used for mutation endpoints (rename, apply-mappings, export) where passing
    large bodies as query params would be awkward.
    """
    if payload is None:
        payload = {}
    url = f"{RECAF_HTTP_BASE}/{endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(trust_env=False) as client:
            resp = await client.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            try:
                return resp.json()
            except json.JSONDecodeError:
                return {"response": resp.text}

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
