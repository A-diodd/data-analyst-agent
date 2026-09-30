from src.sql_graph import run_question_graph

COLUMNS = "orders(order_id, order_status)"


def ok_result(preview):
    return {
        "ok": True,
        "columns": list(preview[0].keys()),
        "preview": preview,
        "row_count": len(preview),
        "data_ref": None,
        "error": None,
        "error_type": None,
        "cached": False,
    }


def test_success_first_try():
    def chat_fn(messages, **kwargs):
        return {"content": "SELECT count(*) AS n FROM orders"}

    def run_fn(sql, schema="olist", timeout_s=10):
        return ok_result([{"n": 99441}])

    out = run_question_graph("有多少订单", chat_fn=chat_fn, run_fn=run_fn, columns=COLUMNS)
    assert out["ok"] is True
    assert out["attempts"] == 1
    assert out["preview"] == [{"n": 99441}]


def test_bad_column_then_fix():
    seen = []

    def chat_fn(messages, **kwargs):
        seen.append(messages[-1]["content"])
        if len(seen) == 1:
            return {"content": "SELECT no_such FROM orders"}
        return {"content": "SELECT order_id FROM orders"}

    def run_fn(sql, schema="olist", timeout_s=10):
        if "no_such" in sql:
            return {
                "ok": False,
                "columns": [],
                "preview": [],
                "row_count": 0,
                "data_ref": None,
                "error": 'column "no_such" does not exist',
                "error_type": "undefined",
                "cached": False,
            }
        return ok_result([{"order_id": "a"}])

    out = run_question_graph("看订单号", chat_fn=chat_fn, run_fn=run_fn, columns=COLUMNS)
    assert out["ok"] is True
    assert out["attempts"] == 2
    assert "does not exist" in seen[1]


def test_give_up_after_max_fixes():
    calls = {"n": 0}

    def chat_fn(messages, **kwargs):
        calls["n"] += 1
        return {"content": "DELETE FROM orders"}

    def run_fn(sql, schema="olist", timeout_s=10):
        raise AssertionError("guard should stop this before the database")

    out = run_question_graph("删掉订单", chat_fn=chat_fn, run_fn=run_fn, columns=COLUMNS)
    assert out["ok"] is False
    assert out["error_type"] == "guard"
    assert calls["n"] == 3