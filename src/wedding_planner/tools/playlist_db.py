"""Chinook sample database tools for the playlist agent and the genre dropdown."""

import sqlite3

from langchain.tools import tool

from ..config import get_settings

FALLBACK_GENRES = ["Jazz", "Blues", "Classical", "Latin", "Pop", "Rock", "Reggae"]


def list_genres() -> list[str]:
    """Genre names from the database, or a short fallback list if it is missing."""
    path = get_settings().chinook_db_path
    try:
        with sqlite3.connect(path) as conn:
            rows = conn.execute("SELECT Name FROM Genre ORDER BY Name").fetchall()
        return [r[0] for r in rows] or FALLBACK_GENRES
    except sqlite3.Error:
        return FALLBACK_GENRES


@tool
def query_playlist_db(query: str) -> str:
    """Query the database for playlist information."""
    from langchain_community.utilities import SQLDatabase

    try:
        db = SQLDatabase.from_uri(f"sqlite:///{get_settings().chinook_db_path}")
        return db.run(query)
    except Exception as exc:
        return f"Error querying database: {exc}"
