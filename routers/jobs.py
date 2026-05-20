"""Print Jobs router — CRUD for print job registrations."""

import datetime
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from routers._templates import templates
from utils.helpers import (
    create_print_job,
    delete_print_job,
    get_all_print_jobs,
    get_job_by_id,
    get_rule_options,
    update_print_job,
)

router = APIRouter(prefix="/jobs")


@router.get("", response_class=HTMLResponse)
def jobs_page(request: Request, edit_id: str | None = None) -> HTMLResponse:
    jobs = get_all_print_jobs().to_dict("records")
    rule_opts = get_rule_options()  # {name: id}
    edit_job = get_job_by_id(edit_id) if edit_id else None
    return templates.TemplateResponse(
        request,
        "jobs.html",
        {
            "request": request,
            "active": "jobs",
            "jobs": jobs,
            "rule_options": rule_opts,
            "edit_job": edit_job,
            "today": str(datetime.date.today()),
            "msg": request.query_params.get("msg"),
            "msg_type": request.query_params.get("type", "success"),
        },
    )


@router.post("")
def create_job_handler(
    id: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    rule_id: Annotated[int | None, Form()] = None,
    print_weight: Annotated[float, Form()] = 0.0,
    print_duration: Annotated[float, Form()] = 0.0,
    operator_time: Annotated[float, Form()] = 0.0,
    modeling_time: Annotated[float, Form()] = 0.0,
    quantity: Annotated[int, Form()] = 1,
    discount: Annotated[float, Form()] = 0.0,
    print_date: Annotated[str, Form()] = "",
    is_personal_use: Annotated[str, Form()] = "",
    customer: Annotated[str, Form()] = "",
    material: Annotated[str, Form()] = "",
) -> RedirectResponse:
    personal = is_personal_use == "1"
    ok, msg = create_print_job(
        {
            "id": id.strip(),
            "description": description.strip(),
            "rule_id": rule_id,
            "print_weight": print_weight,
            "print_duration": print_duration,
            "operator_time": operator_time,
            "modeling_time": modeling_time,
            "quantity": quantity,
            "discount": discount,
            "print_date": print_date or str(datetime.date.today()),
            "is_personal_use": personal,
            "customer": "" if personal else customer.strip(),
            "material": material.strip(),
        }
    )
    if ok:
        return RedirectResponse("/jobs?msg=Print+job+saved&type=success", 303)
    return RedirectResponse(f"/jobs?msg={msg.replace(' ', '+')}&type=error", 303)


@router.post("/{job_id}")
def update_job_handler(
    job_id: str,
    description: Annotated[str, Form()] = "",
    rule_id: Annotated[int | None, Form()] = None,
    print_weight: Annotated[float, Form()] = 0.0,
    print_duration: Annotated[float, Form()] = 0.0,
    operator_time: Annotated[float, Form()] = 0.0,
    modeling_time: Annotated[float, Form()] = 0.0,
    quantity: Annotated[int, Form()] = 1,
    discount: Annotated[float, Form()] = 0.0,
    print_date: Annotated[str, Form()] = "",
    is_personal_use: Annotated[str, Form()] = "",
    customer: Annotated[str, Form()] = "",
    material: Annotated[str, Form()] = "",
) -> RedirectResponse:
    personal = is_personal_use == "1"
    ok, msg = update_print_job(
        job_id,
        {
            "description": description.strip(),
            "rule_id": rule_id,
            "print_weight": print_weight,
            "print_duration": print_duration,
            "operator_time": operator_time,
            "modeling_time": modeling_time,
            "quantity": quantity,
            "discount": discount,
            "print_date": print_date,
            "is_personal_use": personal,
            "customer": "" if personal else customer.strip(),
            "material": material.strip(),
        },
    )
    if ok:
        return RedirectResponse("/jobs?msg=Print+job+updated&type=success", 303)
    return RedirectResponse(f"/jobs?msg={msg.replace(' ', '+')}&type=error", 303)


@router.post("/{job_id}/delete")
def delete_job_handler(job_id: str) -> HTMLResponse:
    """Called via HTMX — returns empty to remove the table row."""
    delete_print_job(job_id)
    return HTMLResponse("")
