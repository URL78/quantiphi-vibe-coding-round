"""
DeepWiki MCP integration — isolated from all other features.

Connects to DeepWiki's MCP server over Streamable HTTP transport.
Uses the official `mcp` Python library when available; falls back to
a direct JSON-RPC/httpx implementation if the library is absent.

Failure in this module must NEVER affect the main GitHub dashboard.
All public functions return (result, error_message) tuples.
"""

import json
import logging
from typing import Any, Dict, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEEPWIKI_URL = settings.deepwiki_mcp_url
REQUEST_TIMEOUT = 30.0  # DeepWiki may take longer than regular API calls


# ─── JSON-RPC helpers (fallback transport) ───────────────────────────────


def _jsonrpc_body(method: str, params: Dict[str, Any], req_id: int = 1) -> Dict:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params,
    }


async def _call_mcp_tool_http(
    tool_name: str, arguments: Dict[str, Any]
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Call a DeepWiki MCP tool using raw httpx (JSON-RPC over HTTP).
    This is the fallback when the `mcp` library is unavailable.
    """
    payload = _jsonrpc_body(
        "tools/call",
        {"name": tool_name, "arguments": arguments},
    )
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(
                DEEPWIKI_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code == 404:
                return None, "DeepWiki: repository not found or not indexed."
            if not resp.is_success:
                return None, f"DeepWiki returned HTTP {resp.status_code}."

            data = resp.json()
            if "error" in data:
                err = data["error"]
                return None, f"DeepWiki error: {err.get('message', str(err))}"

            result = data.get("result")
            return result, None

    except httpx.TimeoutException:
        return None, "DeepWiki request timed out. The repository may not be indexed yet."
    except httpx.RequestError as exc:
        return None, f"DeepWiki connection error: {exc}"
    except Exception as exc:
        logger.exception("Unexpected DeepWiki error: %s", exc)
        return None, f"Unexpected error communicating with DeepWiki: {exc}"


async def _call_mcp_tool(
    tool_name: str, arguments: Dict[str, Any]
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Call a DeepWiki MCP tool. Tries the official mcp library first,
    falls back to direct httpx.
    """
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        async with streamablehttp_client(DEEPWIKI_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                # result.content is a list of TextContent / other content objects
                if result and result.content:
                    texts = [
                        c.text for c in result.content if hasattr(c, "text")
                    ]
                    return "\n".join(texts), None
                return None, "DeepWiki returned an empty response."

    except ImportError:
        logger.debug("mcp library not available, using httpx fallback.")
        return await _call_mcp_tool_http(tool_name, arguments)
    except Exception as exc:
        logger.warning("MCP client error (%s), trying httpx fallback: %s", tool_name, exc)
        return await _call_mcp_tool_http(tool_name, arguments)


# ─── Public API ──────────────────────────────────────────────────────────


async def get_wiki_structure(
    owner: str, repo: str
) -> Tuple[Optional[Any], Optional[str]]:
    """Retrieve repository documentation structure via read_wiki_structure."""
    return await _call_mcp_tool(
        "read_wiki_structure",
        {"repoUrl": f"https://github.com/{owner}/{repo}"},
    )


async def get_wiki_contents(
    owner: str, repo: str
) -> Tuple[Optional[Any], Optional[str]]:
    """Retrieve full repository documentation via read_wiki_contents."""
    return await _call_mcp_tool(
        "read_wiki_contents",
        {"repoUrl": f"https://github.com/{owner}/{repo}"},
    )


async def ask_question(
    owner: str, repo: str, question: str
) -> Tuple[Optional[str], Optional[str]]:
    """Ask a natural-language question about a repository via ask_question tool."""
    return await _call_mcp_tool(
        "ask_question",
        {
            "repoUrl": f"https://github.com/{owner}/{repo}",
            "question": question,
        },
    )
