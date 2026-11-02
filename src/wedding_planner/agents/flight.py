from langchain.agents import create_agent

from ..prompts import load_prompt


def build_flight_agent(model, flight_tools: list):
    return create_agent(model=model, tools=flight_tools, system_prompt=load_prompt("flight_agent"))
