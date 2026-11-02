"""Runs the real coordinator with a scripted model and fake specialists (no network)."""

import asyncio
from datetime import date

from langchain.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult

from wedding_planner import service
from wedding_planner.models import WeddingInputs


class ScriptedModel(BaseChatModel):
    """Plays back a fixed list of AI messages, one per model call."""

    script: list
    index: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        message = self.script[self.index]
        self.index += 1
        return ChatResult(generations=[ChatGeneration(message=message)])


class FakeSpecialist:
    def __init__(self, reply):
        self.reply = reply

    async def ainvoke(self, *_args, **_kwargs):
        return {"messages": [AIMessage(content=self.reply)]}


def call(name, call_id):
    return AIMessage(content="", tool_calls=[{"name": name, "args": {}, "id": call_id, "type": "tool_call"}])


def run_plan(monkeypatch, venue_reply):
    script = [
        call("search_flights", "1"),
        call("search_venues", "2"),
        call("suggest_playlist", "3"),
        AIMessage(content="Final plan"),
    ]
    monkeypatch.setattr(service, "get_model", lambda: ScriptedModel(script=script))

    async def no_tools():
        return []

    monkeypatch.setattr(service, "load_flight_tools", no_tools)
    monkeypatch.setattr(service, "build_flight_agent", lambda *_: FakeSpecialist("Flight list"))
    monkeypatch.setattr(service, "build_venue_agent", lambda *_: FakeSpecialist(venue_reply))
    monkeypatch.setattr(service, "build_playlist_agent", lambda *_: FakeSpecialist("Track list"))

    inputs = WeddingInputs("London", "Paris", 100, "Jazz", date(2099, 6, 12))

    async def collect():
        return [e async for e in service.plan_wedding(inputs)]

    return asyncio.run(collect())


def test_agents_run_in_order_and_results_stream(monkeypatch):
    events = run_plan(monkeypatch, "Venue list")
    pairs = [(e.agent, e.status) for e in events]
    assert pairs == [
        ("flights", "running"), ("flights", "done"),
        ("venues", "running"), ("venues", "done"),
        ("playlist", "running"), ("playlist", "done"),
        ("summary", "done"),
    ]
    assert events[1].content == "Flight list"
    assert events[-1].content == "Final plan"


def test_one_failed_agent_does_not_stop_the_run(monkeypatch):
    events = run_plan(monkeypatch, "ERROR: Search limit reached")
    venue_done = [e for e in events if e.agent == "venues" and e.status != "running"][0]
    assert venue_done.status == "failed"
    assert venue_done.content == "Search limit reached"
    assert events[-1].agent == "summary" and events[-1].status == "done"
