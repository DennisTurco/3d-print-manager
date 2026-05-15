"""
PostgreSQL database — connection helpers and schema initialisation.

Connection is configured via environment variables (loaded from .env):
    DATABASE_URL        → full DSN, e.g. postgresql://admin:admin@localhost:5432/print_manager
                          (takes priority over individual vars below)
    POSTGRES_HOST       → default: localhost
    POSTGRES_PORT       → default: 5432
    POSTGRES_DB         → default: print_manager
    POSTGRES_USER       → default: admin
    POSTGRES_PASSWORD   → default: admin

Business logic (calculations, aggregations) lives in utils/helpers.py.
This module only handles:
  - opening / closing connections
  - creating tables (DDL)
"""

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────────────────────────────────────


def get_dsn() -> str:
    """Return a libpq connection string, preferring DATABASE_URL if set."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'print_manager')} "
        f"user={os.getenv('POSTGRES_USER', 'admin')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'admin')}"
    )


def get_connection() -> psycopg2.extensions.connection:
    """Return a raw psycopg2 connection with RealDictCursor as default factory.

    Caller is responsible for commit / rollback / close.
    Prefer the get_cursor() context manager for transactional work.
    """
    return psycopg2.connect(
        get_dsn(),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


@contextmanager
def get_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """Context manager that yields a cursor inside an auto-committed transaction.

    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM rules WHERE id = %s", (rule_id,))
            rows = cur.fetchall()
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Schema
# ─────────────────────────────────────────────────────────────────────────────


def init_db() -> None:
    """Create all application tables if they do not already exist."""
    with get_cursor() as cur:

        # ── Pricing rules ──────────────────────────────────────────────────
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS rules (
                id               SERIAL PRIMARY KEY,
                name             TEXT    NOT NULL UNIQUE,
                filament_price   REAL    NOT NULL,   -- € per full spool
                spool_weight     REAL    NOT NULL,   -- grams per spool
                electricity_cost REAL    NOT NULL,   -- € / kWh
                printer_power    REAL    NOT NULL,   -- kW
                wear_cost        REAL    NOT NULL,   -- € / hour
                operator_hourly  REAL    NOT NULL,   -- € / hour
                modeling_hourly  REAL    NOT NULL,   -- € / hour
                margin           REAL    NOT NULL,   -- % markup on cost
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ── Print jobs ─────────────────────────────────────────────────────
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS print_jobs (
                id               TEXT PRIMARY KEY,
                description      TEXT,
                rule_id          INTEGER REFERENCES rules(id) ON DELETE SET NULL,
                print_weight     REAL    NOT NULL,   -- grams
                print_duration   REAL    NOT NULL,   -- hours
                operator_time    REAL    NOT NULL DEFAULT 0,  -- hours
                modeling_time    REAL    NOT NULL DEFAULT 0,  -- hours
                quantity         INTEGER NOT NULL DEFAULT 1,
                discount         REAL    NOT NULL DEFAULT 0,  -- %
                print_date       DATE    NOT NULL,
                customer         TEXT,                        -- NULL = personal use
                is_personal_use  BOOLEAN NOT NULL DEFAULT FALSE,
                material         TEXT,
                -- calculated fields — populated by business logic layer
                material_cost    REAL,
                energy_cost      REAL,
                machine_wear     REAL,
                labor_cost       REAL,
                total_cost       REAL,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ── Sales / revenue ────────────────────────────────────────────────
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id              SERIAL PRIMARY KEY,
                customer        TEXT    NOT NULL,
                sale_date       DATE    NOT NULL,
                print_job_id    TEXT    REFERENCES print_jobs(id) ON DELETE SET NULL,
                manual_price    REAL,               -- overrides auto-calculated price
                -- calculated fields — populated by business logic layer
                sale_price      REAL,
                profit          REAL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
