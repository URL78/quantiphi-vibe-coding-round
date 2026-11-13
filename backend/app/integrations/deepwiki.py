"""
DeepWiki MCP integration.

Uses the MCP Streamable HTTP transport (spec 2024-11-05).
Protocol flow:
  1. POST initialize  → get session capabilities + mcp-session-id header
  2. POST notifications/initialized  (no response needed)
  3. POST tools/call  → get answer (JSON or SSE stream)

Falls back gracefully so dashboard is never broken by DeepWiki failures.
All public functions return (result, error_message) tuples.
"""

import json
import logging
from typing import Any, Dict, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEEPWIKI_URL = settings.deepwiki_mcp_url
REQUEST_TIMEOUT = 45.0


# ─── MCP Streamable HTTP transport ───────────────────────────────────────────

def _base_headers(session_id: Optional[str] = None) -> Dict[str, str]:
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "GitHub-Developer-Portfolio/1.0",
    }
    if session_id:
        h["mcp-session-id"] = session_id
    return h


def _parse_sse(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse an SSE stream and extract text content from MCP tool result."""
    collected = []
    for line in text.splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[6:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            msg = json.loads(payload)
            result = msg.get("result", {})
            if isinstance(result, dict):
                for item in result.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        collected.append(item.get("text", ""))
        except (json.JSONDecodeError, TypeError):
            pass
    if collected:
        return "\n".join(collected), None
    return None, "DeepWiki returned an empty response."


def _parse_json_result(data: Dict) -> Tuple[Optional[str], Optional[str]]:
    """Extract text from a JSON-RPC result object."""
    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        return None, f"DeepWiki error: {msg}"

    result = data.get("result", {})

    # Flat text result
    if isinstance(result, str) and result.strip():
        return result.strip(), None

    # MCP CallToolResult shape: { content: [{type:"text", text:"..."}] }
    if isinstance(result, dict):
        content = result.get("content", [])
        texts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        answer = "\n".join(t for t in texts if t)
        if answer:
            return answer, None

    return None, "DeepWiki returned an unexpected response format."


async def _call_mcp_tool(
    tool_name: str, arguments: Dict[str, Any]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Full MCP Streamable HTTP round-trip:
      initialize → initialized notification → tools/call
    """
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:

            # ── Step 1: initialize ────────────────────────────────────────
            init_resp = await client.post(
                DEEPWIKI_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "portfolio-app", "version": "1.0"},
                    },
                },
                headers=_base_headers(),
            )

            if not init_resp.is_success:
                return None, (
                    f"DeepWiki is currently unavailable (HTTP {init_resp.status_code}). "
                    "Try again in a moment."
                )

            # Grab session id if the server sent one
            session_id = (
                init_resp.headers.get("mcp-session-id")
                or init_resp.headers.get("x-session-id")
            )

            # ── Step 2: notifications/initialized ─────────────────────────
            await client.post(
                DEEPWIKI_URL,
                json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                headers=_base_headers(session_id),
            )

            # ── Step 3: tools/call ────────────────────────────────────────
            call_resp = await client.post(
                DEEPWIKI_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                },
                headers=_base_headers(session_id),
            )

            if call_resp.status_code == 404:
                return None, (
                    "This repository has not been indexed by DeepWiki yet. "
                    "DeepWiki indexes popular public repositories. "
                    "Try a well-known repo like facebook/react or microsoft/vscode."
                )

            if not call_resp.is_success:
                return None, f"DeepWiki returned HTTP {call_resp.status_code}."

            content_type = call_resp.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                return _parse_sse(call_resp.text)

            try:
                return _parse_json_result(call_resp.json())
            except Exception:
                # Might be SSE-shaped even without the right content-type
                return _parse_sse(call_resp.text)

    except httpx.TimeoutException:
        return None, (
            "DeepWiki request timed out (45 s). "
            "The repository may not be indexed yet, or DeepWiki is under load."
        )
    except httpx.ConnectError:
        return None, "Could not connect to DeepWiki. Check your internet connection."
    except httpx.RequestError as exc:
        return None, f"DeepWiki connection error: {exc}"
    except Exception as exc:
        logger.exception("Unexpected DeepWiki error for tool %s: %s", tool_name, exc)
        return None, f"Unexpected error: {exc}"


# ─── Public API ───────────────────────────────────────────────────────────────


async def get_wiki_structure(owner: str, repo: str) -> Tuple[Optional[Any], Optional[str]]:
    """Retrieve repository wiki structure from DeepWiki."""
    return await _call_mcp_tool(
        "read_wiki_structure",
        {"repoUrl": f"https://github.com/{owner}/{repo}"},
    )


async def get_wiki_contents(owner: str, repo: str) -> Tuple[Optional[Any], Optional[str]]:
    """Retrieve full wiki contents from DeepWiki."""
    return await _call_mcp_tool(
        "read_wiki_contents",
        {"repoUrl": f"https://github.com/{owner}/{repo}"},
    )


async def ask_question(owner: str, repo: str, question: str) -> Tuple[Optional[str], Optional[str]]:
    """Ask a natural-language question about a repository."""
    return await _call_mcp_tool(
        "ask_question",
        {
            "repoUrl": f"https://github.com/{owner}/{repo}",
            "question": question,
        },
    )
