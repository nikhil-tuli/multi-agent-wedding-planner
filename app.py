"""Streamlit UI for the Wedding Planner Agent."""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from wedding_planner.config import ROOT  # noqa: E402
from wedding_planner.models import MAX_GUESTS, MIN_GUESTS, InvalidInputs, WeddingInputs  # noqa: E402
from wedding_planner.service import plan_wedding  # noqa: E402
from wedding_planner.tools.playlist_db import list_genres  # noqa: E402

STATUS_LABELS = {"waiting": "Waiting", "running": "Running...", "done": "Done", "failed": "Failed"}
AGENTS = [("flights", "Flights"), ("venues", "Venues"), ("playlist", "Playlist"), ("summary", "Coordinator")]

st.set_page_config(page_title="Wedding Planner Agent", layout="wide")

if "results" not in st.session_state:
    st.session_state.results = {}  # agent key -> {"status": ..., "content": ...}
results = st.session_state.results

# ---- Sidebar form -------------------------------------------------------------------------
with st.sidebar:
    st.header("Trip details")
    origin = st.text_input("Origin city", value="London")
    destination = st.text_input("Destination city", value="Paris")
    guest_count = st.number_input("Guest count", min_value=MIN_GUESTS, max_value=MAX_GUESTS, value=100, step=10)
    genres = list_genres()
    genre = st.selectbox("Music genre", genres, index=genres.index("Jazz") if "Jazz" in genres else 0)
    date_start = st.date_input("Wedding date", value=date.today() + timedelta(days=240), min_value=date.today())
    date_end = st.date_input("Latest date (optional)", value=None, min_value=date_start)
    st.caption("Leave the second date empty for a fixed day.")
    submitted = st.button("Plan my wedding", type="primary", use_container_width=True)

# ---- Main layout --------------------------------------------------------------------------
st.title("Wedding Planner Agent")
st.caption("Flights, venues and a playlist, planned by a team of agents.")

status_cols = st.columns(len(AGENTS))
status_slots = {key: col.empty() for (key, _), col in zip(AGENTS, status_cols)}
banner = st.empty()

tab_names = ["Summary", "Flights", "Venues", "Playlist", "Sample output"]
tabs = st.tabs(tab_names)
tab_slots = {}
for key, tab in zip(["summary", "flights", "venues", "playlist"], tabs[:4]):
    with tab:
        tab_slots[key] = st.empty()
with tabs[4]:
    st.markdown((ROOT / "data" / "sample_output.md").read_text(encoding="utf-8"))


def refresh(key: str) -> None:
    """Redraw one agent's status tile and its result tab."""
    entry = results.get(key, {"status": "waiting", "content": ""})
    label = dict(AGENTS)[key]
    status_slots[key].markdown(f"**{label}**  \n{STATUS_LABELS[entry['status']]}")
    slot = tab_slots[key]
    if entry["status"] == "done":
        slot.markdown(entry["content"])
    elif entry["status"] == "failed":
        slot.error(entry["content"] or "This agent could not finish.")
    elif entry["status"] == "running":
        slot.info("Working on it...")
    else:
        slot.info("No results yet. Fill in the trip details and choose Plan my wedding.")


def show_banner() -> None:
    failed = [dict(AGENTS)[k] for k, _ in AGENTS if results.get(k, {}).get("status") == "failed"]
    if failed:
        banner.warning(f"Could not finish: {', '.join(failed)}. The other results are shown in their tabs.")
    else:
        banner.empty()


async def run(inputs: WeddingInputs) -> None:
    async for event in plan_wedding(inputs):
        results[event.agent] = {"status": event.status, "content": event.content}
        refresh(event.agent)
        show_banner()


# ---- Run ----------------------------------------------------------------------------------
if submitted:
    inputs = WeddingInputs(origin, destination, int(guest_count), genre, date_start, date_end)
    try:
        inputs.validate()
    except InvalidInputs as exc:
        st.sidebar.error("\n\n".join(exc.errors))
    else:
        results.clear()
        for key, _ in AGENTS:
            refresh(key)
        asyncio.run(run(inputs))
else:
    for key, _ in AGENTS:
        refresh(key)
    show_banner()
