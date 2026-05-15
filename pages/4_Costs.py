"""
Costs page — detailed cost breakdown per print job (auto-populated from print data).
"""

import streamlit as st

from utils.helpers import get_costs_breakdown, get_costs_totals

st.set_page_config(page_title="Costs · 3D Print Manager", page_icon="💰", layout="wide")

with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="page-title"><i class="fa-solid fa-coins"></i> Costs</h1>', unsafe_allow_html=True)
st.markdown(
    "Detailed cost breakdown for every print job — automatically derived from job data and "
    "the linked pricing rule. No manual input required."
)
st.markdown("---")

# ── Filters ────────────────────────────────────────────────────────────────────
with st.expander("Filters", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        date_from = st.date_input("From date", value=None)
    with fc2:
        date_to = st.date_input("To date", value=None)
    with fc3:
        filter_rule = st.text_input("Rule name contains", placeholder="Any")
    with fc4:
        filter_customer = st.text_input("Customer contains", placeholder="Any")

# ── Cost breakdown table ───────────────────────────────────────────────────────
costs_df = get_costs_breakdown(
    date_from=str(date_from) if date_from else None,
    date_to=str(date_to) if date_to else None,
    rule_name=filter_rule or None,
    customer=filter_customer or None,
)

st.markdown('<div class="section-header"><i class="fa-solid fa-table-list"></i> Cost Breakdown per Job</div>', unsafe_allow_html=True)

if costs_df.empty:
    st.info(
        "No cost data available yet. Register print jobs on the **Print Jobs** page "
        "to populate this table automatically."
    )
else:
    _col_labels = {
        "id":            "Job ID",
        "description":   "Description",
        "rule_name":     "Rule",
        "customer":      "Customer",
        "print_date":    "Date",
        "quantity":      "Qty",
        "material_cost": "Material (€)",
        "energy_cost":   "Energy (€)",
        "machine_wear":  "Machine Wear (€)",
        "labor_cost":    "Labour (€)",
        "total_cost":    "Total Cost (€)",
    }
    available = [c for c in _col_labels if c in costs_df.columns]
    st.dataframe(
        costs_df[available].rename(columns=_col_labels),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f"*{len(costs_df)} job(s) shown.*")

st.markdown("---")

# ── Aggregated totals ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-calculator"></i> Aggregated Cost Totals</div>', unsafe_allow_html=True)

totals = get_costs_totals()

t1, t2, t3, t4, t5 = st.columns(5)

_total_data = [
    (t1, '<i class="fa-solid fa-layer-group"></i> Material',    totals["total_material"]),
    (t2, '<i class="fa-solid fa-bolt"></i> Energy',             totals["total_energy"]),
    (t3, '<i class="fa-solid fa-gear"></i> Machine Wear',       totals["total_wear"]),
    (t4, '<i class="fa-solid fa-user-tie"></i> Labour',         totals["total_labor"]),
    (t5, '<i class="fa-solid fa-calculator"></i> Grand Total',  totals["grand_total"]),
]

for col, label, value in _total_data:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">€ {value:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Cost composition chart ─────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-chart-pie"></i> Cost Composition</div>', unsafe_allow_html=True)

import plotly.graph_objects as go  # noqa: E402

_labels = ["Material", "Energy", "Machine Wear", "Labour"]
_values = [
    totals["total_material"],
    totals["total_energy"],
    totals["total_wear"],
    totals["total_labor"],
]

if sum(_values) == 0:
    st.info("Add print jobs to see the cost composition chart.")
else:
    fig_pie = go.Figure(
        go.Pie(
            labels=_labels,
            values=_values,
            hole=0.45,
            marker_colors=["#FF6B35", "#FBBF24", "#3B82F6", "#22C55E"],
            textinfo="label+percent",
        )
    )
    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1A1D23",
        showlegend=True,
        height=350,
    )
    st.plotly_chart(fig_pie, use_container_width=True)
