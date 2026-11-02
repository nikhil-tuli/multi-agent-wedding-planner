"""Entry point for the UI: run the coordinator and stream each agent's result as it finishes."""

from dataclasses import dataclass
from typing import AsyncIterator

from langchain.messages import AIMessage, HumanMessage, ToolMessage

from .agents.common import ERROR_PREFIX, friendly_error, text_of
from .agents.coordinator import build_coordinator
from .agents.flight import build_flight_agent
from .agents.playlist import build_playlist_agent
from .agents.venue import build_venue_agent
from .config import get_settings
from .llm import get_model
from .models import WeddingInputs
from .prompts import render
from .tools.mcp_flights import load_flight_tools

# Coordinator tool name -> result key shown in the UI
TOOL_TO_AGENT = {
    "search_flights": "flights",
    "search_venues": "venues",
    "suggest_playlist": "playlist",
}
AGENT_ORDER = ["flights", "venues", "playlist", "summary"]


@dataclass(frozen=True)
class PlanEvent:
    agent: str  # "flights" | "venues" | "playlist" | "summary"
    status: str  # "running" | "done" | "failed"
    content: str = ""


async def plan_wedding(inputs: WeddingInputs) -> AsyncIterator[PlanEvent]:
    """Validate inputs, run the agents one at a time, and yield an event as each starts or finishes."""
    inputs.validate()
    settings = get_settings()

    try:
        model = get_model()
        flight_tools = await load_flight_tools()
        coordinator = build_coordinator(
            model,
            build_flight_agent(model, flight_tools),
            build_venue_agent(model),
            build_playlist_agent(model),
        )
        request = {
            "messages": [HumanMessage(content=render("coordinator", **_template_values(inputs)))],
            **inputs.initial_state(),
        }
        config = {"tags": ["wedding-planner"], "recursion_limit": settings.recursion_limit}

        async for chunk in coordinator.astream(request, config=config, stream_mode="updates"):
            for update in chunk.values():
                for message in (update or {}).get("messages", []):
                    for event in _events_from(message):
                        yield event
    except Exception as exc:
        yield PlanEvent("summary", "failed", friendly_error(exc))


def _template_values(inputs: WeddingInputs) -> dict:
    s = inputs.initial_state()
    return {k: s[k] for k in ("origin", "destination", "guest_count", "genre", "dates")}


def _events_from(message):
    if isinstance(message, AIMessage):
        if message.tool_calls:
            for call in message.tool_calls:
                agent = TOOL_TO_AGENT.get(call["name"])
                if agent:
                    yield PlanEvent(agent, "running")
        else:
            text = text_of(message).strip()
            if text:
                yield PlanEvent("summary", "done", text)
    elif isinstance(message, ToolMessage):
        agent = TOOL_TO_AGENT.get(message.name)
        if agent:
            text = text_of(message)
            if text.startswith(ERROR_PREFIX):
                yield PlanEvent(agent, "failed", text.removeprefix(ERROR_PREFIX).strip())
            else:
                yield PlanEvent(agent, "done", text)
