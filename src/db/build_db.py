import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SCHEMA_SQL = ROOT / "sql" / "01_schema.sql"

TABLES = [
    ("olist_orders_dataset.csv", "orders"),
    ("olist_order_items_dataset.csv", "order_items"),
    ("olist_order_payments_dataset.csv", "payments"),
    ("olist_order_reviews_dataset.csv", "reviews"),
    ("olist_customers_dataset.csv", "customers"),
    ("olist_products_dataset.csv", "products"),
    ("olist_sellers_dataset.csv", "sellers"),
    ("olist_geolocation_dataset.csv", "geolocation"),
    ("product_category_name_translation.csv", "category_translation"),
]


def run_script(cur, sql: str) -> None:
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cur.execute(statement)


def main() -> None:
    load_dotenv(ROOT / ".env")
    with psycopg.connect(os.environ["PG_ADMIN_DSN"], autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS olist CASCADE")
            run_script(cur, SCHEMA_SQL.read_text(encoding="utf-8"))
            for filename, table in TABLES:
                path = RAW / filename
                if not path.exists():
                    raise FileNotFoundError(path)
                with cur.copy(
                    f"COPY olist.{table} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
                ) as copy:
                    copy.write(path.read_bytes())
                cur.execute(f"SELECT count(*) FROM olist.{table}")
                print(table, cur.fetchone()[0])
            cur.execute("GRANT USAGE ON SCHEMA olist TO analyst_ro")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA olist TO analyst_ro")


if __name__ == "__main__":
    main()