"""
3D Printing Cost & Profit Management Application
Main Streamlit entry point — home / welcome page.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from database.db import init_db  # noqa: E402

st.set_page_config(
    page_title="3D Print Manager",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
with open("assets/style.css") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# Initialise DB tables on cold start — show a clear error if Postgres is down
try:
    init_db()
except Exception as _db_err:
    st.error(
        f"**Cannot connect to PostgreSQL.** Make sure the Docker container is running.\n\n"
        f"```\ndocker compose up -d\n```\n\n"
        f"Error detail: `{_db_err}`"
    )
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title"><i class="fa-solid fa-cube"></i> 3D Print Manager</h1>', unsafe_allow_html=True)
st.markdown("**Cost & Profit Management for 3D Printing — hobby & small-scale commercial use.**")
st.markdown("---")

# ── Navigation tiles ──────────────────────────────────────────────────────────
cols = st.columns(5)

_TILES = [
    ("fa-solid fa-sliders",        "Rules",      "Define reusable pricing profiles for filament, energy, wear & labour."),
    ("fa-solid fa-print",          "Print Jobs", "Register every print run and see an automatic cost breakdown."),
    ("fa-solid fa-coins",          "Costs",      "Detailed cost report per job, automatically derived from print data."),
    ("fa-solid fa-cash-register",  "Sales",      "Log customer sales, track revenue and compute profit per item."),
    ("fa-solid fa-gauge-high",     "Dashboard",  "Analytics overview: trends, top prints and printer utilisation."),
]

_PAGES = [
    "pages/2_Rules.py",
    "pages/3_Print_Jobs.py",
    "pages/4_Costs.py",
    "pages/5_Sales.py",
    "pages/1_Dashboard.py",
]

for col, (icon, name, desc), page in zip(cols, _TILES, _PAGES):
    with col:
        st.markdown(
            f"""
            <div class="home-tile">
                <div class="tile-icon"><i class="{icon}"></i></div>
                <div class="tile-title">{name}</div>
                <div class="tile-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Open {name}", use_container_width=True)

st.markdown("---")
st.caption("v1.0.0 · 3D Print Manager")
