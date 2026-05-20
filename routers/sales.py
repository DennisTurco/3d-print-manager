"""Sales router — CRUD for revenue tracking."""

import datetime
import json
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from routers._templates import templates
from utils.helpers import (
    create_sale,
    delete_sale,
    get_all_sales,
    get_print_job_ids,
    get_sales_summary,
)

router = APIRouter(prefix="/sales")


@router.get("", response_class=HTMLResponse)
def sales_page(request: Request) -> HTMLResponse:
    sales = get_all_sales().to_dict("records")
    summary = get_sales_summary()
    job_ids = get_print_job_ids()

    profit_data = json.dumps(
        {
            "labels": [str(s.get("id", "")) for s in sales],
            "values": [float(s.get("profit") or 0) for s in sales],
        }
    )

    return templates.TemplateResponse(
        request,
        "sales.html",
        {
            "request": request,
            "active": "sales",
            "sales": sales,
            "summary": summary,
            "job_ids": job_ids,
            "today": str(datetime.date.today()),
            "has_profit_chart": len(sales) > 0,
            "profit_data": profit_data,
            "msg": request.query_params.get("msg"),
            "msg_type": request.query_params.get("type", "success"),
        },
    )


@router.post("")
def create_sale_handler(
    customer: Annotated[str, Form()],
    sale_date: Annotated[str, Form()],
    print_job_id: Annotated[str, Form()],
    manual_price: Annotated[float, Form()] = 0.0,
) -> RedirectResponse:
    if not customer.strip():
        return RedirectResponse("/sales?msg=Customer+name+is+required&type=error", 303)
    if not print_job_id:
        return RedirectResponse("/sales?msg=A+print+job+must+be+selected&type=error", 303)

    ok, msg = create_sale(
        {
            "customer": customer.strip(),
            "sale_date": sale_date or str(datetime.date.today()),
            "print_job_id": print_job_id,
            "manual_price": manual_price if manual_price > 0 else None,
        }
    )
    if ok:
        return RedirectResponse("/sales?msg=Sale+recorded+successfully&type=success", 303)
    return RedirectResponse(f"/sales?msg={msg.replace(' ', '+')}&type=error", 303)


@router.post("/{sale_id}/delete")
def delete_sale_handler(sale_id: int) -> HTMLResponse:
    """Called via HTMX — returns empty to remove the table row."""
    delete_sale(sale_id)
    return HTMLResponse("")
