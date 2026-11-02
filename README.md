# Wedding Planner Agent

A basic tool and a first attempt at getting several AI agents to work together.

## Objective

Enter where you are travelling from, where the wedding is, how many guests, a music genre and a date. The app returns flight options, venue ideas and a playlist, plus a short combined plan.

## Key features

- One form for origin, destination, guest count, genre and dates
- Three specialist agents (flights, venues, playlist) managed by a coordinator agent
- Results appear tab by tab as each agent finishes
- A Sample output tab shows what a finished plan looks like
- Model and provider can be changed in `.env` without touching code

## How the app works

The coordinator agent saves your inputs, then asks the specialists for help one at a time: flights, venues, then playlist. If one fails, the others still show their results. The coordinator then writes a short final plan.

```
Form -> Coordinator -> Flight agent   (Kiwi flight search)
                    -> Venue agent    (web search)
                    -> Playlist agent (sample music database)
                    -> Final plan
```

## Tools and models used

- Streamlit for the interface
- LangChain agents (Python)
- Groq `openai/gpt-oss-120b` by default, configurable
- Kiwi MCP server for flights
- Tavily for web search
- Chinook sample database for music (not a real music catalogue)

## Usage

1. Install: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your `GROQ_API_KEY` and `TAVILY_API_KEY`
3. Run: `streamlit run app.py`
4. Fill in the trip details in the sidebar and choose **Plan my wedding**

Prompts are plain markdown files in `prompts/`. Run the tests with `pytest`.

Note: free-tier model limits are small, so a full run can take a minute or two while the app waits and retries.
