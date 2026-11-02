from langchain.agents import create_agent

from ..prompts import load_prompt
from ..tools.playlist_db import query_playlist_db


def build_playlist_agent(model):
    return create_agent(model=model, tools=[query_playlist_db], system_prompt=load_prompt("playlist_agent"))
