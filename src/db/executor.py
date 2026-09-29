import os

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg import errors

_pool: ConnectionPool | None = None

#拿到一个数据库连接，这里最多能并行拿到四个连接
def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        load_dotenv()
        _pool = ConnectionPool(
            os.environ["PG_RO_DSN"],
            min_size=1,
            max_size=4,
            kwargs={"autocommit": False},
        )
        _pool.open()
    return _pool

#确定sql失败的错误
def classify_error(exc: Exception) -> str:
    if isinstance(exc, (errors.SyntaxError,)):
        return "syntax"
    if isinstance(exc, (errors.UndefinedColumn, errors.UndefinedTable, errors.UndefinedFunction, errors.UndefinedObject)):
        return "undefined"
    if isinstance(exc, errors.QueryCanceled):
        return "timeout"
    if isinstance(exc, (errors.InsufficientPrivilege, errors.ReadOnlySqlTransaction)):
        return "permission"
    return "other"

#跑sql查询，查的是olist这个库同时设置超时时间为10秒
def run_sql(sql: str, schema: str = "olist", timeout_s: float = 10) -> dict:
    try:
        with get_pool().connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT set_config('search_path', %s, true)", (schema,))
                cur.execute(
                    "SELECT set_config('statement_timeout', %s, true)",
                    (str(int(timeout_s * 1000)),),
                )
                cur.execute(sql)
                if cur.description is None:
                    conn.rollback()
                    return {
                        "ok": False,
                        "columns": [],
                        "preview": [],
                        "row_count": 0,
                        "data_ref": None,
                        "error": "only SELECT is expected",
                        "error_type": "other",
                        "cached": False,
                    }
                rows = cur.fetchall()
            conn.commit()
    except Exception as exc:
        return {
            "ok": False,
            "columns": [],
            "preview": [],
            "row_count": 0,
            "data_ref": None,
            "error": str(exc).strip(),
            "error_type": classify_error(exc),
            "cached": False,
        }

    preview = rows[:20]
    columns = list(preview[0].keys()) if preview else []
    return {
        "ok": True,
        "columns": columns,
        "preview": preview,
        "row_count": len(rows),
        "data_ref": None,
        "error": None,
        "error_type": "empty" if not rows else None,
        "cached": False,
    }