
import sqlglot

from src.guard.sql_guard import check_sql


def limit_of(sql: str) -> int | None:
    limit = sqlglot.parse_one(sql, read="postgres").args.get("limit")
    if limit is None:
        return None
    return int(limit.expression.this)


def test_drop():
    assert check_sql("DROP TABLE orders", "olist").ok is False


def test_delete():
    assert check_sql("DELETE FROM orders", "olist").ok is False


def test_update():
    assert check_sql("UPDATE orders SET order_status = 'x'", "olist").ok is False


def test_two_statements():
    assert check_sql("SELECT 1; DROP TABLE orders", "olist").ok is False


def test_pg_read_file():
    assert check_sql("SELECT pg_read_file('/etc/passwd')", "olist").ok is False


def test_pg_sleep():
    assert check_sql("SELECT pg_sleep(20)", "olist").ok is False


def test_copy():
    assert check_sql("COPY orders TO STDOUT", "olist").ok is False


def test_set():
    assert check_sql("SET statement_timeout = 0", "olist").ok is False


def test_do():
    assert check_sql("DO $$ BEGIN PERFORM 1; END $$;", "olist").ok is False


def test_cross_schema_app():
    assert check_sql("SELECT * FROM app.secret", "olist").ok is False


def test_cross_schema_catalog():
    assert check_sql("SELECT * FROM pg_catalog.pg_user", "olist").ok is False


def test_statement_hidden_in_comment():
    assert check_sql("SELECT 1; /* note */ DELETE FROM orders", "olist").ok is False


def test_legal_cte():
    result = check_sql("WITH t AS (SELECT 1 AS n) SELECT * FROM t", "olist")
    assert result.ok is True
    assert limit_of(result.sql) == 5000


def test_legal_window():
    sql = "SELECT sum(price) OVER (PARTITION BY order_id) FROM order_items"
    result = check_sql(sql, "olist")
    assert result.ok is True
    assert limit_of(result.sql) == 5000


def test_limit_is_capped():
    result = check_sql("SELECT * FROM orders LIMIT 99999", "olist")
    assert result.ok is True
    assert limit_of(result.sql) == 5000