"""User inputs and their validation."""

from dataclasses import dataclass
from datetime import date

MIN_GUESTS = 10
MAX_GUESTS = 500


class InvalidInputs(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class WeddingInputs:
    origin: str
    destination: str
    guest_count: int
    genre: str
    date_start: date
    date_end: date | None = None

    def validate(self, today: date | None = None) -> None:
        today = today or date.today()
        errors = []
        if not self.origin.strip():
            errors.append("Enter an origin city.")
        if not self.destination.strip():
            errors.append("Enter a destination city.")
        if self.origin.strip() and self.origin.strip().lower() == self.destination.strip().lower():
            errors.append("Origin and destination must be different.")
        if not MIN_GUESTS <= self.guest_count <= MAX_GUESTS:
            errors.append(f"Guest count must be between {MIN_GUESTS} and {MAX_GUESTS}.")
        if not self.genre.strip():
            errors.append("Choose a music genre.")
        if self.date_start < today:
            errors.append("The wedding date must be today or later.")
        if self.date_end is not None and self.date_end < self.date_start:
            errors.append("The latest date must be on or after the wedding date.")
        if errors:
            raise InvalidInputs(errors)

    def dates_text(self) -> str:
        if self.date_end is None or self.date_end == self.date_start:
            return f"on {self.date_start.isoformat()}"
        return f"between {self.date_start.isoformat()} and {self.date_end.isoformat()}"

    def initial_state(self) -> dict:
        """Values placed in the coordinator's state so tools can read them."""
        return {
            "origin": self.origin.strip(),
            "destination": self.destination.strip(),
            "guest_count": str(self.guest_count),
            "genre": self.genre.strip(),
            "dates": self.dates_text(),
        }
