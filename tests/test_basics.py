from datetime import date

import pytest
from mcp.types import CallToolResult, TextContent

from wedding_planner.models import InvalidInputs, WeddingInputs
from wedding_planner.prompts import load_prompt, load_templates, render
from wedding_planner.tools.mcp_flights import truncate_result
from wedding_planner.tools.playlist_db import list_genres

TODAY = date(2026, 11, 2)


def make(**overrides):
    values = dict(
        origin="London", destination="Paris", guest_count=100, genre="Jazz",
        date_start=date(2027, 6, 12), date_end=None,
    )
    values.update(overrides)
    return WeddingInputs(**values)


def test_valid_inputs_pass():
    make().validate(today=TODAY)


@pytest.mark.parametrize(
    "overrides",
    [
        {"origin": " "},
        {"destination": "london"},
        {"guest_count": 5},
        {"guest_count": 501},
        {"genre": ""},
        {"date_start": date(2026, 1, 1)},
        {"date_end": date(2027, 6, 1)},
    ],
)
def test_invalid_inputs_raise(overrides):
    with pytest.raises(InvalidInputs):
        make(**overrides).validate(today=TODAY)


def test_dates_text():
    assert make().dates_text() == "on 2027-06-12"
    assert make(date_end=date(2027, 6, 20)).dates_text() == "between 2027-06-12 and 2027-06-20"


@pytest.mark.parametrize("name", ["coordinator", "flight_agent", "venue_agent", "playlist_agent"])
def test_system_prompts_exist(name):
    assert load_prompt(name)


def test_templates_render_with_their_placeholders():
    values = make().initial_state()
    for name in load_templates():
        assert render(name, **values)


def test_template_missing_value_raises():
    with pytest.raises(KeyError):
        render("flight", origin="London")


def test_truncate_result_caps_text():
    result = CallToolResult(content=[TextContent(type="text", text="x" * 50)], isError=False)
    truncated = truncate_result(result, 10)
    assert truncated.content[0].text.startswith("x" * 10)
    assert len(truncated.content[0].text) < 50


def test_genres_come_from_database():
    assert "Jazz" in list_genres()
