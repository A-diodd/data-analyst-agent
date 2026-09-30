"""同一套循环，画成三个格子：生成、检查、执行。"""

from typing import TypedDict

from langgraph.graph import END, StateGraph

from src.config import MAX_SQL_FIX, MODEL
from src.guard.sql_guard import check_sql
from src.sql_loop import SYSTEM, extract_sql

#定义状态
class SqlState(TypedDict):
    question: str
    columns: str
    schema: str
    feedback: str | None
    sql: str | None
    attempts: int   #已尝试次数
    ok: bool
    preview: list
    error: str | None
    error_type: str | None

#建图
def build_sql_graph(chat_fn, run_fn):
    #生成节点，得到用户问题和列清单，让模型生成问题对应的sql语句
    def generate(state: SqlState) -> dict:
        user = state["question"] + "\n\n列清单：\n" + state["columns"]
        if state["feedback"]:
            user += "\n\n上一轮的错误：\n" + state["feedback"]
        reply = chat_fn(
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            model=MODEL,
        )
        return {"sql": extract_sql(reply["content"]), "attempts": state["attempts"] + 1} #更新状态sql和attempts

    #门卫节点，对问题生成的sql进行检查
    def guard(state: SqlState) -> dict:
        guarded = check_sql(state["sql"], state["schema"])  #检查入口
        if not guarded.ok:
            return {
                "ok": False,
                "preview": [],
                "error": guarded.reason,
                "error_type": "guard",
                "feedback": f"{guarded.reason}\nSQL:\n{state['sql']}",  #出现错误及时返回
            }
        return {"sql": guarded.sql, "error": None, "error_type": None, "feedback": None}

    def execute(state: SqlState) -> dict:      #执行节点，执行门卫通过的sql语句，真的sql查询
        result = run_fn(state["sql"], schema=state["schema"])
        ok = result["ok"] and result["error_type"] != "empty"
        return {
            "ok": ok,
            "preview": result["preview"],
            "error": result["error"],
            "error_type": result["error_type"],
            "feedback": None if ok else (result["error"] or "query returned no rows"),
        }
 
    #门卫这里的分支，如果sql语句通过就去执行节点，如果没有通过就去生成节点，同时如果尝试次数超过最大次数就返回结束
    def after_guard(state: SqlState) -> str:
        if state["error_type"] != "guard":
            return "execute"
        if state["attempts"] >= MAX_SQL_FIX + 1:
            return "end"
        return "generate"

    #执行这里也有分支，如果查询的结果是ok或者是尝试次数超过最大次数就返回结束，如果没有通过就去生成节点
    def after_execute(state: SqlState) -> str:
        if state["ok"] or state["attempts"] >= MAX_SQL_FIX + 1:
            return "end"
        return "generate"

    graph = StateGraph(SqlState)
    graph.add_node("generate", generate)
    graph.add_node("guard", guard)
    graph.add_node("execute", execute)
    graph.set_entry_point("generate")
    graph.add_edge("generate", "guard")
    graph.add_conditional_edges(
        "guard",
        after_guard,
        {"execute": "execute", "generate": "generate", "end": END},
    )
    graph.add_conditional_edges(
        "execute",
        after_execute,
        {"generate": "generate", "end": END},
    )
    return graph.compile()


def run_question_graph(question: str, *, chat_fn, run_fn, columns: str, schema: str = "olist") -> dict:
    state = build_sql_graph(chat_fn, run_fn).invoke(
        {
            "question": question,
            "columns": columns,
            "schema": schema,
            "feedback": None,
            "sql": None,
            "attempts": 0,
            "ok": False,
            "preview": [],
            "error": None,
            "error_type": None,
        }
    )
    return {
        "ok": state["ok"],
        "sql": state["sql"],
        "preview": state["preview"],
        "attempts": state["attempts"],
        "error": state["error"],
        "error_type": state["error_type"],
    }