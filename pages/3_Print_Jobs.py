"""
Print Jobs page — register print runs and view automatic cost breakdowns.
"""

import datetime

import streamlit as st

from utils.helpers import (
    create_print_job,
    delete_print_job,
    get_all_print_jobs,
    get_rule_options,
)

st.set_page_config(page_title="Print Jobs · 3D Print Manager", page_icon="🖨️", layout="wide")

with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="page-title"><i class="fa-solid fa-print"></i> Print Jobs</h1>', unsafe_allow_html=True)
st.markdown(
    "Register every print run. Costs are computed automatically from the linked pricing rule."
)
st.markdown("---")

# ── Add new job form ───────────────────────────────────────────────────────────
with st.expander("Register New Print Job", expanded=True):
    rule_options = get_rule_options()  # {name: id}

    with st.form("add_job_form", clear_on_submit=True):
        st.markdown('<div class="section-header"><i class="fa-solid fa-plus"></i> New Print Job</div>', unsafe_allow_html=True)

        # Row 1 — identifiers
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            job_id = st.text_input(
                "Unique Job ID *",
                placeholder="e.g. PJ-2024-001",
                help="Manually assigned identifier — must be unique.",
            )
        with r1c2:
            description = st.text_input(
                "Description",
                placeholder="e.g. Articulated dragon, 0.2 mm PLA",
            )
        with r1c3:
            selected_rule = st.selectbox(
                "Pricing Rule *",
                options=list(rule_options.keys()) if rule_options else [],
                index=None,
                placeholder="Select a rule…",
                help="All cost fields are derived from the chosen rule.",
            )

        # Row 2 — physical parameters
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1:
            print_weight = st.number_input(
                "Print Weight (g) *",
                min_value=0.0, value=50.0, step=1.0, format="%.1f",
            )
        with r2c2:
            print_duration = st.number_input(
                "Print Duration (h) *",
                min_value=0.0, value=3.0, step=0.25, format="%.2f",
            )
        with r2c3:
            operator_time = st.number_input(
                "Operator Work Time (h)",
                min_value=0.0, value=0.25, step=0.25, format="%.2f",
                help="Time spent preparing / post-processing the print.",
            )
        with r2c4:
            modeling_time = st.number_input(
                "Modeling / Design Time (h)",
                min_value=0.0, value=0.0, step=0.25, format="%.2f",
            )

        # Row 3 — commercial parameters
        r3c1, r3c2, r3c3, r3c4, r3c5 = st.columns(5)
        with r3c1:
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        with r3c2:
            discount = st.number_input(
                "Discount (%)",
                min_value=0.0, max_value=100.0, value=0.0, step=1.0,
            )
        with r3c3:
            print_date = st.date_input("Print Date *", value=datetime.date.today())
        with r3c4:
            customer = st.text_input("Customer", placeholder="Optional")
        with r3c5:
            material = st.text_input(
                "Material",
                placeholder="e.g. PLA, PETG, ABS",
            )

        st.markdown("---")

        # ── Calculated cost preview (read-only) ────────────────────────────────
        st.markdown(
            '<p><i class="fa-solid fa-calculator"></i> <strong>Calculated Costs</strong> — automatically filled when saved.</p>',
            unsafe_allow_html=True,
        )
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        with pc1:
            st.text_input("Material Cost (€)", value="—", disabled=True)
        with pc2:
            st.text_input("Energy Cost (€)", value="—", disabled=True)
        with pc3:
            st.text_input("Machine Wear (€)", value="—", disabled=True)
        with pc4:
            st.text_input("Labour Cost (€)", value="—", disabled=True)
        with pc5:
            st.text_input("Total Production Cost (€)", value="—", disabled=True)

        save_btn = st.form_submit_button("Save Print Job", type="primary", use_container_width=True)

        if save_btn:
            errors = []
            if not job_id.strip():
                errors.append("Job ID is required.")
            if not selected_rule:
                errors.append("A pricing rule must be selected.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                ok, msg = create_print_job(
                    {
                        "id":             job_id.strip(),
                        "description":    description.strip(),
                        "rule_id":        rule_options.get(selected_rule),
                        "print_weight":   print_weight,
                        "print_duration": print_duration,
                        "operator_time":  operator_time,
                        "modeling_time":  modeling_time,
                        "quantity":       quantity,
                        "discount":       discount,
                        "print_date":     str(print_date),
                        "customer":       customer.strip(),
                        "material":       material.strip(),
                    }
                )
                if ok:
                    st.success(f"Print job **{job_id}** saved!")
                    st.rerun()
                else:
                    st.error(msg)

st.markdown("---")

# ── Jobs table ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-table-list"></i> All Print Jobs</div>', unsafe_allow_html=True)

# Optional filters
with st.expander("Filters", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_customer = st.text_input("Customer contains", placeholder="Any")
    with fc2:
        filter_material = st.text_input("Material contains", placeholder="Any")
    with fc3:
        filter_date_range = st.date_input(
            "Print date range",
            value=[],
            help="Select a start and end date to filter results.",
        )

jobs_df = get_all_print_jobs()

if jobs_df.empty:
    st.info("No print jobs registered yet. Use the form above to add your first job.")
else:
    # Apply UI filters (filtering logic will be fully active once helpers are implemented)
    filtered_df = jobs_df.copy()
    if filter_customer:
        mask = filtered_df.get("customer", "").str.contains(filter_customer, case=False, na=False)
        filtered_df = filtered_df[mask]
    if filter_material:
        mask = filtered_df.get("material", "").str.contains(filter_material, case=False, na=False)
        filtered_df = filtered_df[mask]

    _col_labels = {
        "id":            "Job ID",
        "description":   "Description",
        "rule_name":     "Rule",
        "print_date":    "Date",
        "customer":      "Customer",
        "material":      "Material",
        "quantity":      "Qty",
        "print_weight":  "Weight (g)",
        "print_duration":"Duration (h)",
        "material_cost": "Material (€)",
        "energy_cost":   "Energy (€)",
        "machine_wear":  "Wear (€)",
        "labor_cost":    "Labour (€)",
        "total_cost":    "Total Cost (€)",
    }
    available_cols = [c for c in _col_labels if c in filtered_df.columns]
    st.dataframe(
        filtered_df[available_cols].rename(columns=_col_labels),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(f"*{len(filtered_df)} job(s) shown.*")

    # ── Delete job ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header"><i class="fa-solid fa-trash"></i> Delete a Print Job</div>', unsafe_allow_html=True)

    job_ids = jobs_df["id"].tolist()
    del_id = st.selectbox(
        "Select job ID to delete",
        options=job_ids,
        index=None,
        placeholder="Choose a job…",
    )
    if del_id:
        st.warning(
            f"Deleting **{del_id}** will also remove any linked sales records."
        )
        if st.button("Confirm Delete", type="primary"):
            ok = delete_print_job(del_id)
            if ok:
                st.success(f"Job {del_id} deleted.")
                st.rerun()
            else:
                st.error("Delete failed.")
