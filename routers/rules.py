"""Rules router — CRUD for pricing profiles."""

from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from routers._templates import templates
from utils.helpers import (
    create_rule,
    delete_rule,
    get_all_rules,
    get_rule_by_id,
    update_rule,
)

router = APIRouter(prefix="/rules")


@router.get("", response_class=HTMLResponse)
def rules_page(request: Request, edit_id: int | None = None) -> HTMLResponse:
    rules = get_all_rules().to_dict("records")
    edit_rule = get_rule_by_id(edit_id) if edit_id else None
    return templates.TemplateResponse(
        request,
        "rules.html",
        {
            "request": request,
            "active": "rules",
            "rules": rules,
            "edit_rule": edit_rule,
            "msg": request.query_params.get("msg"),
            "msg_type": request.query_params.get("type", "success"),
        },
    )


@router.post("")
def create_rule_handler(
    name: Annotated[str, Form()],
    filament_price: Annotated[float, Form()],
    spool_weight: Annotated[float, Form()],
    electricity_cost: Annotated[float, Form()],
    printer_power: Annotated[float, Form()],
    wear_cost: Annotated[float, Form()],
    operator_hourly: Annotated[float, Form()],
    modeling_hourly: Annotated[float, Form()],
    margin: Annotated[float, Form()],
) -> RedirectResponse:
    ok = create_rule(
        {
            "name": name.strip(),
            "filament_price": filament_price,
            "spool_weight": spool_weight,
            "electricity_cost": electricity_cost,
            "printer_power": printer_power,
            "wear_cost": wear_cost,
            "operator_hourly": operator_hourly,
            "modeling_hourly": modeling_hourly,
            "margin": margin,
        }
    )
    if ok:
        return RedirectResponse("/rules?msg=Rule+saved+successfully&type=success", 303)
    return RedirectResponse("/rules?msg=Failed+to+save+rule+(name+may+already+exist)&type=error", 303)


@router.post("/{rule_id}")
def update_rule_handler(
    rule_id: int,
    name: Annotated[str, Form()],
    filament_price: Annotated[float, Form()],
    spool_weight: Annotated[float, Form()],
    electricity_cost: Annotated[float, Form()],
    printer_power: Annotated[float, Form()],
    wear_cost: Annotated[float, Form()],
    operator_hourly: Annotated[float, Form()],
    modeling_hourly: Annotated[float, Form()],
    margin: Annotated[float, Form()],
) -> RedirectResponse:
    ok = update_rule(
        rule_id,
        {
            "name": name.strip(),
            "filament_price": filament_price,
            "spool_weight": spool_weight,
            "electricity_cost": electricity_cost,
            "printer_power": printer_power,
            "wear_cost": wear_cost,
            "operator_hourly": operator_hourly,
            "modeling_hourly": modeling_hourly,
            "margin": margin,
        },
    )
    if ok:
        return RedirectResponse("/rules?msg=Rule+updated&type=success", 303)
    return RedirectResponse("/rules?msg=Update+failed&type=error", 303)


@router.post("/{rule_id}/delete")
def delete_rule_handler(rule_id: int) -> HTMLResponse:
    """Called via HTMX — returns empty to remove the table row."""
    delete_rule(rule_id)
    return HTMLResponse("")
