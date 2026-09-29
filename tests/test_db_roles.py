import os

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg.errors import InsufficientPrivilege, QueryCanceled, ReadOnlySqlTransaction

load_dotenv()


@pytest.fixture
def ro_conn():
    with psycopg.connect(os.environ["PG_RO_DSN"], autocommit=True) as conn:
        yield conn


def test_readonly_blocks_insert(ro_conn):
    with pytest.raises(ReadOnlySqlTransaction):
        ro_conn.execute("INSERT INTO orders (order_id) VALUES ('x')")


def test_cross_schema_blocked(ro_conn):
    with pytest.raises(InsufficientPrivilege):
        ro_conn.execute("SELECT * FROM app.secret")


def test_statement_timeout(ro_conn):
    with pytest.raises(QueryCanceled):
        ro_conn.execute("SELECT pg_sleep(20)")