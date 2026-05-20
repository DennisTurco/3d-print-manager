"""Dashboard router — GET /"""

import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routers._templates import templates
from utils.helpers import (
    get_all_print_jobs,
    get_dashboard_kpis,
    get_monthly_trends,
    get_printer_utilization,
    get_top_profitable_jobs,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    kpis = get_dashboard_kpis()

    trends_list = get_monthly_trends().to_dict("records")
    top_list = get_top_profitable_jobs(10).to_dict("records")
    util_list = get_printer_utilization().to_dict("records")

    jobs_df = get_all_print_jobs()
    if not jobs_df.empty and "print_date" in jobs_df.columns:
        recent = jobs_df.sort_values("print_date", ascending=False).head(10).to_dict("records")
    else:
        recent = []

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "active": "dashboard",
            "kpis": kpis,
            "has_trends": len(trends_list) > 0,
            "trends_json": json.dumps(trends_list, default=str),
            "has_top": len(top_list) > 0,
            "top_json": json.dumps(top_list, default=str),
            "has_util": len(util_list) > 0,
            "util_json": json.dumps(util_list, default=str),
            "recent_jobs": recent,
        },
    )
