"""Helpers shared by the agents and the service."""

from langchain.messages import HumanMessage

from ..config import get_settings

ERROR_PREFIX = "ERROR:"


def friendly_error(exc: Exception) -> str:
    """Turn provider errors into a short message for the UI."""
    text = str(exc)
    lowered = text.lower()
    if "429" in text or "rate limit" in lowered or "rate_limit" in lowered:
        return "Rate limit reached for the language model. Wait a minute and try again."
    if "413" in text or "request too large" in lowered:
        return "The request was too large for the model's limit. Try again or use a model with a higher limit."
    if "api key" in lowered or "401" in text:
        return "The API key was rejected. Check the keys in your .env file."
    return text[:300] or exc.__class__.__name__


def text_of(message) -> str:
    """Plain text of a message, whether its content is a string or a list of blocks."""
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)


async def run_specialist(agent, message: str) -> str:
    """Run a specialist agent. Errors come back as text so one failure does not stop the run."""
    try:
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"recursion_limit": get_settings().recursion_limit},
        )
        return text_of(response["messages"][-1]) or f"{ERROR_PREFIX} The agent returned no answer."
    except Exception as exc:
        return f"{ERROR_PREFIX} {friendly_error(exc)}"
