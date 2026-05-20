"""Costs router — read-only cost breakdown view."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routers._templates import templates
from utils.helpers import get_costs_breakdown, get_costs_totals

router = APIRouter(prefix="/costs")


@router.get("", response_class=HTMLResponse)
def costs_page(request: Request) -> HTMLResponse:
    qp = request.query_params
    breakdown = get_costs_breakdown(
        date_from=qp.get("from") or None,
        date_to=qp.get("to") or None,
        rule_name=qp.get("rule") or None,
        customer=qp.get("customer") or None,
    ).to_dict("records")

    totals = get_costs_totals()

    pie_data = json.dumps(
        {
            "labels": ["Material", "Energy", "Machine Wear", "Labour"],
            "values": [
                totals["total_material"],
                totals["total_energy"],
                totals["total_wear"],
                totals["total_labor"],
            ],
        }
    )

    return templates.TemplateResponse(
        request,
        "costs.html",
        {
            "request": request,
            "active": "costs",
            "breakdown": breakdown,
            "totals": totals,
            "has_pie": sum(
                [totals["total_material"], totals["total_energy"],
                 totals["total_wear"],    totals["total_labor"]]
            ) > 0,
            "pie_data": pie_data,
            "f_from":     qp.get("from", ""),
            "f_to":       qp.get("to", ""),
            "f_rule":     qp.get("rule", ""),
            "f_customer": qp.get("customer", ""),
        },
    )
