# 3D Print Manager

> **Python + Streamlit desktop application for 3D printing cost & profit management.**
> Designed for hobby and small-scale commercial use.

## Pages

| Page | Description |
|---------|-------------|
| **Rules** | Define reusable pricing profiles — filament, electricity, machine wear, labour and margin |
| **Print Jobs** | Register every print run (commercial or personal use); costs auto-calculated from the linked rule |
| **Costs** | Detailed cost breakdown per job with aggregated totals and a composition chart |
| **Sales** | Log customer sales; sale price and profit are computed automatically |
| **Dashboard** | KPIs, monthly profit trends, most profitable prints, printer utilisation stats |

> **Personal use prints** are fully supported. Toggle *Personal Use* when registering a job — no customer is required and the entry is excluded from the Sales page.

## Getting Started

### 1. Clone the project

```bash
git clone <repo-url>
cd 3d-print-manager
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` if you want custom credentials - the defaults work out of the box:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=print_manager
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

# Or use a single connection URL (takes priority over the vars above):
# DATABASE_URL=postgresql://admin:admin@localhost:5432/print_manager
```

### 3. Start PostgreSQL with Docker

```bash
docker compose up -d
```

This pulls `postgres:16-alpine`, starts a container named `print_manager_db`, and
persists all data in a named Docker volume (`postgres_data`).

| Command | Effect |
|---------|--------|
| `docker compose ps` | Check container status |
| `docker compose logs -f db` | Stream Postgres logs |
| `docker compose stop` | Stop container, keep data |
| `docker compose down` | Remove container, keep volume |
| `docker compose down -v` | Remove container **and wipe all data** |

### 4. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the app

**Browser mode (development)**

```bash
streamlit run app.py
```

**Desktop app**

```bash
python launcher.py
```

`launcher.py` starts Streamlit in headless mode and wraps it inside a native
OS window via **pywebview** (1 440 × 920 px, resizable).

## Implementing the Business Logic

All data operations are **stubbed** in `utils/helpers.py`. Every function has a
correct signature, type hints, and a docstring — but the body is a `TODO`.

Your job is to fill in each function using the `get_cursor()` context manager:

```python
from database.db import get_cursor

def get_all_rules() -> pd.DataFrame:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM rules ORDER BY name")
        rows = cur.fetchall()          # returns list[RealDictRow]
    return pd.DataFrame(rows)

def create_rule(rule_data: dict) -> bool:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO rules
                (name, filament_price, spool_weight, electricity_cost,
                 printer_power, wear_cost, operator_hourly, modeling_hourly, margin)
            VALUES
                (%(name)s, %(filament_price)s, %(spool_weight)s, %(electricity_cost)s,
                 %(printer_power)s, %(wear_cost)s, %(operator_hourly)s,
                 %(modeling_hourly)s, %(margin)s)
            """,
            rule_data,
        )
    return True
```

> **psycopg2 placeholders:** use `%s` (positional) or `%(key)s` (named dict) — **not** `?` like SQLite.  
> `get_cursor()` auto-commits on success and rolls back on any exception.

### Key functions to implement

| Function | Description |
|-------|-------------|
| `create_rule` | `INSERT INTO rules` |
| `get_all_rules` | `SELECT * FROM rules` |
| `update_rule` | `UPDATE rules SET … WHERE id = %s` |
| `delete_rule` | `DELETE FROM rules WHERE id = %s` |
| `create_print_job` | Calculate all cost fields, then `INSERT INTO print_jobs` |
| `get_all_print_jobs` | `SELECT pj.*, r.name FROM print_jobs pj LEFT JOIN rules r ON …` |
| `create_sale` | Compute `sale_price` & `profit`, then `INSERT INTO sales` |
| `get_dashboard_kpis` | Aggregate totals across `print_jobs` + `sales` |
| `get_monthly_trends` | `GROUP BY DATE_TRUNC('month', …)` |

### Cost formulas

```txt
material_cost  = (print_weight / spool_weight) × filament_price
energy_cost    = print_duration × printer_power × electricity_cost
machine_wear   = print_duration × wear_cost
labor_cost     = (operator_time × operator_hourly) + (modeling_time × modeling_hourly)
total_cost     = (material_cost + energy_cost + machine_wear + labor_cost) × quantity

sale_price     = total_cost × (1 + margin / 100) × (1 − discount / 100)
profit         = sale_price − total_cost
```

## Database Schema

```sql
-- Pricing profiles
CREATE TABLE rules (
    id               SERIAL PRIMARY KEY,
    name             TEXT    UNIQUE NOT NULL,
    filament_price   REAL    NOT NULL,   -- € per full spool
    spool_weight     REAL    NOT NULL,   -- grams
    electricity_cost REAL    NOT NULL,   -- € / kWh
    printer_power    REAL    NOT NULL,   -- kW
    wear_cost        REAL    NOT NULL,   -- € / hour
    operator_hourly  REAL    NOT NULL,   -- € / hour
    modeling_hourly  REAL    NOT NULL,   -- € / hour
    margin           REAL    NOT NULL,   -- %
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Print jobs (commercial and personal use)
CREATE TABLE print_jobs (
    id               TEXT PRIMARY KEY,
    description      TEXT,
    rule_id          INTEGER REFERENCES rules(id) ON DELETE SET NULL,
    print_weight     REAL    NOT NULL,   -- grams
    print_duration   REAL    NOT NULL,   -- hours
    operator_time    REAL    NOT NULL DEFAULT 0,
    modeling_time    REAL    NOT NULL DEFAULT 0,
    quantity         INTEGER NOT NULL DEFAULT 1,
    discount         REAL    NOT NULL DEFAULT 0,  -- %
    print_date       DATE    NOT NULL,
    customer         TEXT,                        -- NULL when is_personal_use = TRUE
    is_personal_use  BOOLEAN NOT NULL DEFAULT FALSE,
    material         TEXT,
    -- auto-calculated by business logic
    material_cost    REAL,
    energy_cost      REAL,
    machine_wear     REAL,
    labor_cost       REAL,
    total_cost       REAL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales / revenue
CREATE TABLE sales (
    id              SERIAL PRIMARY KEY,
    customer        TEXT    NOT NULL,
    sale_date       DATE    NOT NULL,
    print_job_id    TEXT    REFERENCES print_jobs(id) ON DELETE SET NULL,
    manual_price    REAL,                -- overrides the auto-calculated price
    -- auto-calculated by business logic
    sale_price      REAL,
    profit          REAL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📄 License

MIT — feel free to use, modify and distribute.
