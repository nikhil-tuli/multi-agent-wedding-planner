"""Web search tool for the venue agent, with a per-run search limit."""

from typing import Any

from langchain.tools import tool

MAX_SNIPPET_CHARS = 500
MAX_RESULTS = 4


def make_web_search(max_searches: int):
    """Return a web_search tool that stops after max_searches calls."""
    count = 0

    @tool
    def web_search(query: str) -> dict[str, Any]:
        """Search the web for information. Use plain text characters only in the query
        (for example 'capacite', not 'capacité')."""
        nonlocal count
        count += 1
        if count > max_searches:
            return {"message": "Search limit reached. Summarize your findings and give your final answer."}
        try:
            from tavily import TavilyClient

            response = TavilyClient().search(query, max_results=MAX_RESULTS)
        except Exception as exc:
            return {"error": str(exc)}
        return {
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": (r.get("content") or "")[:MAX_SNIPPET_CHARS],
                }
                for r in response.get("results", [])
            ]
        }

    return web_search
