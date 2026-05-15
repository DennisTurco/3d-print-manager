"""
Dashboard page — analytics overview.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.helpers import (
    get_dashboard_kpis,
    get_monthly_trends,
    get_printer_utilization,
    get_top_profitable_jobs,
)

st.set_page_config(page_title="Dashboard · 3D Print Manager", page_icon="📊", layout="wide")

with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="page-title"><i class="fa-solid fa-gauge-high"></i> Dashboard</h1>', unsafe_allow_html=True)
st.markdown("Business analytics overview — revenue, costs, profit and printer utilisation.")
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────
kpis = get_dashboard_kpis()

k1, k2, k3, k4, k5, k6 = st.columns(6)

_kpi_data = [
    (k1, '<i class="fa-solid fa-euro-sign"></i> Total Revenue',    f"€ {kpis['total_revenue']:,.2f}",    "All-time sales"),
    (k2, '<i class="fa-solid fa-industry"></i> Total Costs',       f"€ {kpis['total_costs']:,.2f}",      "Production costs"),
    (k3, '<i class="fa-solid fa-arrow-trend-up"></i> Net Profit',  f"€ {kpis['net_profit']:,.2f}",       "Revenue − costs"),
    (k4, '<i class="fa-solid fa-bullseye"></i> Profit Margin',     f"{kpis['profit_margin_pct']:.1f} %", "Average margin"),
    (k5, '<i class="fa-solid fa-print"></i> Print Jobs',           str(kpis["num_jobs"]),                "Total registered"),
    (k6, '<i class="fa-regular fa-clock"></i> Print Hours',        f"{kpis['total_print_hours']:.1f} h", "Total machine time"),
]

for col, label, value, sub in _kpi_data:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Monthly trends chart ───────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-calendar-days"></i> Monthly Profit Trends</div>', unsafe_allow_html=True)

trends_df = get_monthly_trends()

if trends_df.empty:
    st.info("No sales data yet — monthly trend chart will appear here once you log sales.")
    # Placeholder figure
    fig_trend = go.Figure()
    fig_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1A1D23",
        plot_bgcolor="#1A1D23",
        height=300,
        annotations=[
            {
                "text": "No data available",
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 18, "color": "#6B7280"},
            }
        ],
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    fig_trend = px.line(
        trends_df,
        x="month",
        y=["revenue", "costs", "profit"],
        labels={"value": "€", "month": "Month", "variable": "Metric"},
        color_discrete_map={"revenue": "#FF6B35", "costs": "#EF4444", "profit": "#22C55E"},
        template="plotly_dark",
    )
    fig_trend.update_layout(
        paper_bgcolor="#1A1D23",
        plot_bgcolor="#1A1D23",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ── Top profitable jobs + Printer utilisation ─────────────────────────────────
col_top, col_util = st.columns(2)

# Most profitable jobs
with col_top:
    st.markdown('<div class="section-header"><i class="fa-solid fa-trophy"></i> Most Profitable Jobs</div>', unsafe_allow_html=True)

    top_df = get_top_profitable_jobs(limit=10)

    if top_df.empty:
        st.info("No profit data available yet.")
        fig_top = go.Figure()
        fig_top.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1A1D23",
            plot_bgcolor="#1A1D23",
            height=320,
            annotations=[
                {
                    "text": "No data available",
                    "xref": "paper", "yref": "paper",
                    "x": 0.5, "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16, "color": "#6B7280"},
                }
            ],
        )
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        fig_top = px.bar(
            top_df,
            x="profit",
            y="description",
            orientation="h",
            color="profit",
            color_continuous_scale="Oranges",
            labels={"profit": "Profit (€)", "description": ""},
            template="plotly_dark",
        )
        fig_top.update_layout(
            paper_bgcolor="#1A1D23",
            plot_bgcolor="#1A1D23",
            height=320,
            showlegend=False,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_top, use_container_width=True)

# Printer utilisation
with col_util:
    st.markdown('<div class="section-header"><i class="fa-solid fa-clock"></i> Printer Utilisation</div>', unsafe_allow_html=True)

    util_df = get_printer_utilization()

    if util_df.empty:
        st.info("No utilisation data available yet.")
        fig_util = go.Figure()
        fig_util.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1A1D23",
            plot_bgcolor="#1A1D23",
            height=320,
            annotations=[
                {
                    "text": "No data available",
                    "xref": "paper", "yref": "paper",
                    "x": 0.5, "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16, "color": "#6B7280"},
                }
            ],
        )
        st.plotly_chart(fig_util, use_container_width=True)
    else:
        fig_util = px.bar(
            util_df,
            x="month",
            y="total_hours",
            color="num_jobs",
            color_continuous_scale="Blues",
            labels={"total_hours": "Hours", "month": "Month", "num_jobs": "Jobs"},
            template="plotly_dark",
        )
        fig_util.update_layout(
            paper_bgcolor="#1A1D23",
            plot_bgcolor="#1A1D23",
            height=320,
        )
        st.plotly_chart(fig_util, use_container_width=True)

st.markdown("---")

# ── Recent activity summary table ─────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-clock-rotate-left"></i> Recent Print Jobs</div>', unsafe_allow_html=True)

from utils.helpers import get_all_print_jobs  # noqa: E402

recent_df = get_all_print_jobs()
if recent_df.empty:
    st.info("No print jobs registered yet.")
else:
    _cols = ["id", "description", "print_date", "customer", "total_cost"]
    available = [c for c in _cols if c in recent_df.columns]
    st.dataframe(
        recent_df[available].sort_values("print_date", ascending=False).head(10),
        use_container_width=True,
        hide_index=True,
    )
