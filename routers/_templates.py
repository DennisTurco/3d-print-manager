"""
Shared Jinja2 Templates instance with custom filters.
Import `templates` from here in every router.
"""

from pathlib import Path

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


# ── Custom filters ────────────────────────────────────────────────────────────

def _currency(value) -> str:
    if value is None:
        return "—"
    try:
        return f"€ {float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _number(value, decimals: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def _percentage(value, decimals: int = 1) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{decimals}f} %"
    except (TypeError, ValueError):
        return "—"


templates.env.filters["currency"] = _currency
templates.env.filters["number"] = _number
templates.env.filters["percentage"] = _percentage
