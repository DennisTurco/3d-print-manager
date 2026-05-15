"""
Sales / Revenue page — log customer sales and track profit.
"""

import datetime

import streamlit as st

from utils.helpers import (
    create_sale,
    delete_sale,
    get_all_sales,
    get_print_job_ids,
    get_sales_summary,
)

st.set_page_config(page_title="Sales · 3D Print Manager", page_icon="💵", layout="wide")

with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="page-title"><i class="fa-solid fa-cash-register"></i> Sales & Revenue</h1>', unsafe_allow_html=True)
st.markdown(
    "Log customer sales linked to print jobs. "
    "Sale price and profit are computed automatically from the job's cost and margin."
)
st.markdown("---")

# ── Add sale form + summary side by side ──────────────────────────────────────
form_col, summary_col = st.columns([2, 1])

with form_col:
    with st.expander("Register New Sale", expanded=True):
        job_ids = get_print_job_ids()

        with st.form("add_sale_form", clear_on_submit=True):
            st.markdown('<div class="section-header">New Sale</div>', unsafe_allow_html=True)

            sc1, sc2 = st.columns(2)
            with sc1:
                customer = st.text_input(
                    "Customer *",
                    placeholder="e.g. Mario Rossi",
                )
                sale_date = st.date_input("Sale Date *", value=datetime.date.today())

            with sc2:
                linked_job = st.selectbox(
                    "Linked Print Job *",
                    options=job_ids if job_ids else [],
                    index=None,
                    placeholder="Select a print job…",
                    help="The cost and margin of this job are used to compute the sale price.",
                )
                manual_price = st.number_input(
                    "Manual Price Override (€)",
                    min_value=0.0, value=0.0, step=0.5, format="%.2f",
                    help=(
                        "Leave at 0.00 to use the auto-calculated price "
                        "(total_cost × margin × (1 − discount))."
                    ),
                )

            st.markdown("---")

            # Auto-calculated preview fields (read-only)
            st.markdown(
                '<p><i class="fa-solid fa-calculator"></i> <strong>Calculated Sale Fields</strong> — filled automatically when saved.</p>',
                unsafe_allow_html=True,
            )
            calc1, calc2 = st.columns(2)
            with calc1:
                st.text_input("Auto Sale Price (€)", value="—", disabled=True)
            with calc2:
                st.text_input("Profit (€)", value="—", disabled=True)

            save_btn = st.form_submit_button(
                "Save Sale", type="primary", use_container_width=True
            )

            if save_btn:
                errors = []
                if not customer.strip():
                    errors.append("Customer name is required.")
                if not linked_job:
                    errors.append("A linked print job is required.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = create_sale(
                        {
                            "customer":      customer.strip(),
                            "sale_date":     str(sale_date),
                            "print_job_id":  linked_job,
                            "manual_price":  manual_price if manual_price > 0 else None,
                        }
                    )
                    if ok:
                        st.success(f"Sale for **{customer}** saved!")
                        st.rerun()
                    else:
                        st.error(msg)

with summary_col:
    st.markdown('<div class="section-header"><i class="fa-solid fa-chart-bar"></i> Sales Summary</div>', unsafe_allow_html=True)

    summary = get_sales_summary()

    _summary_items = [
        ('<i class="fa-solid fa-euro-sign"></i> Total Revenue', f"€ {summary['total_revenue']:,.2f}"),
        ('<i class="fa-solid fa-industry"></i> Total Cost',     f"€ {summary['total_cost']:,.2f}"),
        ('<i class="fa-solid fa-arrow-trend-up"></i> Net Profit', f"€ {summary['net_profit']:,.2f}"),
        ('<i class="fa-solid fa-receipt"></i> Sales Count',     str(summary["num_sales"])),
    ]

    for label, value in _summary_items:
        st.markdown(
            f"""
            <div class="kpi-card" style="margin-bottom:0.7rem;">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Sales table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-table-list"></i> All Sales</div>', unsafe_allow_html=True)

sales_df = get_all_sales()

if sales_df.empty:
    st.info("No sales recorded yet. Use the form above to log your first sale.")
else:
    _col_labels = {
        "id":            "Sale ID",
        "customer":      "Customer",
        "sale_date":     "Date",
        "print_job_id":  "Job ID",
        "description":   "Job Description",
        "manual_price":  "Manual Price (€)",
        "sale_price":    "Sale Price (€)",
        "profit":        "Profit (€)",
    }
    available = [c for c in _col_labels if c in sales_df.columns]
    st.dataframe(
        sales_df[available].rename(columns=_col_labels),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f"*{len(sales_df)} sale(s) recorded.*")

    # ── Delete sale ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header"><i class="fa-solid fa-trash"></i> Delete a Sale</div>', unsafe_allow_html=True)

    sale_ids = sales_df["id"].tolist()
    del_id = st.selectbox(
        "Select sale ID to delete",
        options=sale_ids,
        index=None,
        placeholder="Choose a sale…",
    )
    if del_id:
        if st.button("Confirm Delete", type="primary"):
            ok = delete_sale(int(del_id))
            if ok:
                st.success("Sale deleted.")
                st.rerun()
            else:
                st.error("Delete failed.")

st.markdown("---")

# ── Profit per sale chart ──────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-chart-line"></i> Profit per Sale</div>', unsafe_allow_html=True)

import plotly.graph_objects as go  # noqa: E402

if sales_df.empty or "profit" not in sales_df.columns or sales_df["profit"].isna().all():
    st.info("Profit chart will appear here once sales data is available.")
else:
    fig = go.Figure(
        go.Bar(
            x=sales_df["id"].astype(str),
            y=sales_df["profit"],
            marker_color="#FF6B35",
            text=sales_df["profit"].apply(lambda v: f"€ {v:,.2f}"),
            textposition="auto",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1A1D23",
        plot_bgcolor="#1A1D23",
        xaxis_title="Sale ID",
        yaxis_title="Profit (€)",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)
