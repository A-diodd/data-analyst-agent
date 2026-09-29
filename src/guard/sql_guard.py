"""SQL 守卫。
模型写出的句子先经过这里，再交给 run_sql。
这里只看文字，不连接数据库。
名单永远不全，挡不住的由只读账号负责。
"""

from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

BANNED_FUNCTIONS = {
    "pg_sleep",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_dir",
    "lo_import",
    "lo_export",
    "dblink",
    "set_config",
    "pg_terminate_backend",
    "pg_cancel_backend",
}

QUERY_TYPES = (exp.Select, exp.Union, exp.Intersect, exp.Except)


#门卫的查询结果
@dataclass
class GuardResult:
    ok: bool
    sql: str
    reason: str | None = None


def check_sql(sql: str, allowed_schema: str, max_limit: int = 5000) -> GuardResult:
    try:
        statements = [item for item in sqlglot.parse(sql, read="postgres") if item is not None]
    except ParseError as exc:
        return GuardResult(False, sql, str(exc))
    if len(statements) != 1:
        return GuardResult(False, sql, "only one statement is allowed")
    tree = statements[0]
    if not isinstance(tree, QUERY_TYPES):
        return GuardResult(False, sql, f"only SELECT is allowed, got {type(tree).__name__}")
    for table in tree.find_all(exp.Table):  #查看这句sql语句的表名是否是允许的
        schema_name = str(table.db or "")
        if schema_name and schema_name.lower() != allowed_schema.lower():
            return GuardResult(False, sql, f"schema {schema_name} is not allowed")
    for func in tree.find_all(exp.Func):
        if _function_name(func) in BANNED_FUNCTIONS:
            return GuardResult(False, sql, f"function {_function_name(func)} is not allowed")
    tree = _cap_limit(tree, max_limit)
    return GuardResult(True, tree.sql(dialect="postgres"), None)



def _function_name(func: exp.Func) -> str:
    if isinstance(func, exp.Anonymous):
        raw = func.this if isinstance(func.this, str) else func.sql_name()
        return str(raw).split(".")[-1].lower()
    return func.sql_name().lower()


def _cap_limit(tree: exp.Expression, max_limit: int) -> exp.Expression:
    limit = tree.args.get("limit")
    if limit is None:
        return tree.limit(max_limit)
    value = limit.expression
    if isinstance(value, exp.Literal) and value.is_int and int(value.this) <= max_limit:
        return tree
    tree.set("limit", exp.Limit(expression=exp.Literal.number(max_limit)))
    return tree