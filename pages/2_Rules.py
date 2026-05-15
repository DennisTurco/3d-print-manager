"""
Rules page — define and manage reusable pricing profiles.
"""

import streamlit as st

from utils.helpers import (
    create_rule,
    delete_rule,
    get_all_rules,
    update_rule,
)

st.set_page_config(page_title="Rules · 3D Print Manager", page_icon="⚙️", layout="wide")

with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="page-title"><i class="fa-solid fa-sliders"></i> Pricing Rules</h1>', unsafe_allow_html=True)
st.markdown(
    "Define reusable pricing profiles (filament, electricity, wear, labour) "
    "that can be applied to any print job."
)
st.markdown("---")

# ── Add new rule form ──────────────────────────────────────────────────────────
with st.expander("Add New Rule", expanded=True):
    with st.form("add_rule_form", clear_on_submit=True):
        st.markdown('<div class="section-header"><i class="fa-solid fa-plus"></i> New Pricing Rule</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            rule_name = st.text_input(
                "Rule Name *",
                placeholder="e.g. PLA Standard",
                help="Unique identifier for this pricing profile.",
            )
            filament_price = st.number_input(
                "Filament Spool Price (€)",
                min_value=0.0, value=20.0, step=0.5, format="%.2f",
                help="Total purchase price of one spool.",
            )
            spool_weight = st.number_input(
                "Spool Weight (g)",
                min_value=1.0, value=1000.0, step=50.0,
                help="Net filament weight of the spool in grams.",
            )

        with c2:
            electricity_cost = st.number_input(
                "Electricity Cost (€ / kWh)",
                min_value=0.0, value=0.25, step=0.01, format="%.3f",
            )
            printer_power = st.number_input(
                "Printer Power Consumption (kW)",
                min_value=0.0, value=0.30, step=0.05, format="%.3f",
                help="Average power draw of the printer during a job.",
            )
            wear_cost = st.number_input(
                "Machine Wear Cost (€ / hour)",
                min_value=0.0, value=0.50, step=0.10, format="%.2f",
                help="Estimated hourly cost of printer wear and maintenance.",
            )

        with c3:
            operator_hourly = st.number_input(
                "Operator Hourly Rate (€ / hour)",
                min_value=0.0, value=15.0, step=1.0, format="%.2f",
            )
            modeling_hourly = st.number_input(
                "Modeling / Design Hourly Rate (€ / hour)",
                min_value=0.0, value=25.0, step=1.0, format="%.2f",
            )
            margin = st.number_input(
                "Pricing Margin (%)",
                min_value=0.0, max_value=1000.0, value=30.0, step=1.0,
                help="Percentage mark-up applied on top of the total production cost.",
            )

        submitted = st.form_submit_button("Save Rule", type="primary", use_container_width=True)

        if submitted:
            if not rule_name.strip():
                st.error("Rule name is required.")
            else:
                ok = create_rule(
                    {
                        "name": rule_name.strip(),
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
                    st.success(f"Rule **{rule_name}** saved successfully!")
                    st.rerun()
                else:
                    st.error("Could not save rule — the name may already exist.")

st.markdown("---")

# ── Existing rules table ───────────────────────────────────────────────────────
st.markdown('<div class="section-header"><i class="fa-solid fa-list"></i> Existing Rules</div>', unsafe_allow_html=True)

rules_df = get_all_rules()

if rules_df.empty:
    st.info("No pricing rules defined yet. Use the form above to create your first profile.")
else:
    _col_labels = {
        "name":             "Rule Name",
        "filament_price":   "Spool Price (€)",
        "spool_weight":     "Spool Weight (g)",
        "electricity_cost": "Electricity (€/kWh)",
        "printer_power":    "Power (kW)",
        "wear_cost":        "Wear (€/h)",
        "operator_hourly":  "Operator (€/h)",
        "modeling_hourly":  "Modeling (€/h)",
        "margin":           "Margin (%)",
    }

    display_df = rules_df[[c for c in _col_labels if c in rules_df.columns]].rename(
        columns=_col_labels
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Edit / Delete ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><i class="fa-solid fa-pen-to-square"></i> Edit or Delete a Rule</div>', unsafe_allow_html=True)

    rule_names = rules_df["name"].tolist()
    selected = st.selectbox(
        "Select a rule to manage",
        options=rule_names,
        index=None,
        placeholder="Choose a rule…",
    )

    if selected:
        row = rules_df[rules_df["name"] == selected].iloc[0]
        edit_col, del_col = st.columns([4, 1])

        # ── Edit form ──────────────────────────────────────────────────────────
        with edit_col:
            with st.form("edit_rule_form"):
                st.markdown(f"**Editing:** {selected}")
                ec1, ec2, ec3 = st.columns(3)

                with ec1:
                    e_filament = st.number_input("Spool Price (€)",       value=float(row["filament_price"]),   format="%.2f")
                    e_weight   = st.number_input("Spool Weight (g)",      value=float(row["spool_weight"]))
                    e_elec     = st.number_input("Electricity (€/kWh)",   value=float(row["electricity_cost"]), format="%.3f")

                with ec2:
                    e_power    = st.number_input("Printer Power (kW)",    value=float(row["printer_power"]),    format="%.3f")
                    e_wear     = st.number_input("Machine Wear (€/h)",    value=float(row["wear_cost"]),        format="%.2f")
                    e_operator = st.number_input("Operator (€/h)",        value=float(row["operator_hourly"]),  format="%.2f")

                with ec3:
                    e_modeling = st.number_input("Modeling (€/h)",        value=float(row["modeling_hourly"]),  format="%.2f")
                    e_margin   = st.number_input("Margin (%)",            value=float(row["margin"]),           format="%.1f")

                upd_btn = st.form_submit_button("Update Rule", type="primary", use_container_width=True)

                if upd_btn:
                    ok = update_rule(
                        int(row["id"]),
                        {
                            "filament_price":   e_filament,
                            "spool_weight":     e_weight,
                            "electricity_cost": e_elec,
                            "printer_power":    e_power,
                            "wear_cost":        e_wear,
                            "operator_hourly":  e_operator,
                            "modeling_hourly":  e_modeling,
                            "margin":           e_margin,
                        },
                    )
                    if ok:
                        st.success("Rule updated!")
                        st.rerun()
                    else:
                        st.error("Update failed.")

        # ── Delete ─────────────────────────────────────────────────────────────
        with del_col:
            st.markdown("<br><br><br>", unsafe_allow_html=True)

            if st.button("Delete", use_container_width=True):
                st.session_state["pending_delete_rule"] = selected

            if st.session_state.get("pending_delete_rule") == selected:
                st.warning(f"Delete **{selected}**?")
                if st.button("Yes, delete", type="primary", use_container_width=True):
                    ok = delete_rule(int(row["id"]))
                    if ok:
                        st.success("Deleted.")
                        st.session_state.pop("pending_delete_rule", None)
                        st.rerun()
                    else:
                        st.error("Delete failed.")
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pop("pending_delete_rule", None)
                    st.rerun()
