"""Loads system prompts and user-message templates from the prompts/ folder."""

import re

from .config import ROOT

PROMPTS_DIR = ROOT / "prompts"


def load_prompt(name: str) -> str:
    """Return the system prompt in prompts/<name>.md."""
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


def load_templates() -> dict[str, str]:
    """Return the user-message templates in prompts/user_messages.md, keyed by '## name' headings."""
    text = (PROMPTS_DIR / "user_messages.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (\w+)\s*$", text, flags=re.MULTILINE)
    # parts = [preamble, name1, body1, name2, body2, ...]
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def render(name: str, **values: str) -> str:
    """Fill a user-message template. Raises KeyError if a placeholder has no value."""
    return load_templates()[name].format(**values)
