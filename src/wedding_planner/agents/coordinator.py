"""The coordinator agent. Its tools hand work to the three specialists."""

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool

from ..prompts import load_prompt, render
from ..state import WeddingState
from .common import run_specialist


def build_coordinator(model, flight_agent, venue_agent, playlist_agent):
    @tool
    async def search_flights(runtime: ToolRuntime) -> str:
        """Travel agent searches for flights to the wedding destination."""
        s = runtime.state
        message = render("flight", origin=s["origin"], destination=s["destination"], dates=s["dates"])
        return await run_specialist(flight_agent, message)

    @tool
    async def search_venues(runtime: ToolRuntime) -> str:
        """Venue agent chooses the best venues for the destination and guest count."""
        s = runtime.state
        message = render("venue", destination=s["destination"], guest_count=s["guest_count"])
        return await run_specialist(venue_agent, message)

    @tool
    async def suggest_playlist(runtime: ToolRuntime) -> str:
        """Playlist agent curates a playlist for the chosen genre."""
        message = render("playlist", genre=runtime.state["genre"])
        return await run_specialist(playlist_agent, message)

    return create_agent(
        model=model,
        tools=[search_flights, search_venues, suggest_playlist],
        state_schema=WeddingState,
        system_prompt=load_prompt("coordinator"),
    )
