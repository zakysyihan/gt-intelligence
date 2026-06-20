"""Load SQLite product data into DuckDB for WrenAI engine.

On startup, attaches the SQLite database and creates an in-memory DuckDB
table that the WrenAI engine can query. This bridges the gap between
our SQLite storage and WrenAI's DuckDB-native engine.

ponytail: Using DuckDB's ATTACH is a single SQL statement — no pandas
intermediary, no CSV export. The SQLite file stays untouched.
"""

import sqlite3
from pathlib import Path

import duckdb


def load_sqlite_to_duckdb(sqlite_path: str | Path) -> duckdb.DuckDBPyConnection:
    """Load products from SQLite into an in-memory DuckDB database.

    Returns a DuckDB connection with a 'products' table ready for queries.
    The SQLite file is read-only — no modifications.
    """
    sqlite_path = Path(sqlite_path).resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    # Create in-memory DuckDB
    con = duckdb.connect(":memory:")

    # Install and load sqlite extension, then attach and copy
    con.install_extension("sqlite")
    con.load_extension("sqlite")

    con.execute(f"ATTACH '{sqlite_path}' AS sqlite_db (READ_ONLY)")
    con.execute("CREATE TABLE products AS SELECT * FROM sqlite_db.products")
    con.execute("DETACH sqlite_db")

    # Verify
    row_count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if row_count == 0:
        raise ValueError(f"Loaded 0 rows from {sqlite_path}")

    print(f"[data_loader] Loaded {row_count} products into DuckDB")
    return con


def get_schema_info(con: duckdb.DuckDBPyConnection) -> dict:
    """Return schema metadata for the products table."""
    columns = con.execute("PRAGMA table_info('products')").fetchall()
    schema = {}
    for col in columns:
        schema[col[1]] = {
            "type": col[2],
            "notnull": bool(col[3]),
            "default": col[4],
        }

    row_count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    return {"table": "products", "columns": schema, "row_count": row_count}
