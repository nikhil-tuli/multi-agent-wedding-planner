"""Flight search through the Kiwi MCP server, with retries and size-capped results."""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.shared.exceptions import McpError
from mcp.types import CallToolResult, TextContent

from ..config import get_settings

RETRYABLE_MCP_CODES = {-32603}


def truncate_result(result, max_chars: int):
    """Trim long text blocks so tool output does not blow the model's token limit."""
    if isinstance(result, CallToolResult):
        for item in result.content:
            if isinstance(item, TextContent) and len(item.text) > max_chars:
                item.text = item.text[:max_chars] + "\n...[truncated]"
    return result


def _error_result(message: str) -> CallToolResult:
    # isError stays False so the agent sees the message and can adjust its call.
    return CallToolResult(content=[TextContent(type="text", text=message)], isError=False)


class RetryMCPInterceptor:
    """Retry transient MCP failures, truncate results, and return errors to the agent."""

    def __init__(self, max_retries: int = 3, max_chars: int = 3000):
        self.max_retries = max_retries
        self.max_chars = max_chars

    async def __call__(self, request, handler):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return truncate_result(await handler(request), self.max_chars)
            except McpError as exc:
                last_error = exc
                if exc.error.code not in RETRYABLE_MCP_CODES:
                    return _error_result(f"Tool call failed (non-retryable): {exc}")
            except Exception as exc:
                last_error = exc
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2**attempt)
        return _error_result(f"Tool call failed after {self.max_retries} attempts: {last_error}")


async def load_flight_tools() -> list:
    """Connect to the Kiwi MCP server and return the flight search tool."""
    s = get_settings()
    client = MultiServerMCPClient(
        {"travel_server": {"transport": "streamable_http", "url": s.mcp_url}},
        tool_interceptors=[RetryMCPInterceptor(s.mcp_max_retries, s.mcp_max_result_chars)],
    )
    tools = await client.get_tools()
    # Only the search tool is needed; extra tool schemas cost tokens on every call.
    return [t for t in tools if t.name == "search-flight"] or tools
