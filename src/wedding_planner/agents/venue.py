from langchain.agents import create_agent

from ..config import get_settings
from ..prompts import load_prompt
from ..tools.web_search import make_web_search


def build_venue_agent(model):
    search = make_web_search(get_settings().max_venue_searches)
    return create_agent(model=model, tools=[search], system_prompt=load_prompt("venue_agent"))
