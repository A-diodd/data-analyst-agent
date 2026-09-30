"""让模型写 SQL，门卫和数据库说了算。
第一次就把列清单给模型，它才知道有哪些表。
失败时只附上一轮的错误和同一份列清单。
run_sql 只回前 20 行，所以列清单写在这里，不从查询结果里截。
"""

from src.config import MODEL, MAX_SQL_FIX
from src.guard.sql_guard import check_sql

COLUMNS = """
orders(order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date)
order_items(order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
payments(order_id, payment_sequential, payment_type, payment_installments, payment_value)
reviews(review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp)
customers(customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
products(product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
sellers(seller_id, seller_zip_code_prefix, seller_city, seller_state)
geolocation(geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state)
category_translation(product_category_name, product_category_name_english)
""".strip()

SYSTEM = """你是 PostgreSQL 查询助手。
只输出一条 SELECT，不要解释，不要用 markdown。
表都在 schema olist 中。不要写别的 schema。
列名必须照列清单原文，包括拼写错误。
"""


#模型的回复里面扣出我们想要的那条sql语句
def extract_sql(text:str) -> str:
    text = text.strip()
    if "```" not  in text:
        return text
    body = text.split("```",2)[1]
    if body.lower().startswith("sql"):
        body = body[3:]
    return body.strip()

def run_question(question: str, *, chat_fn, run_fn, columns: str, schema: str = "olist") -> dict:
    feedback = None  #指示上一轮的回馈
    last = {   #兜底返回结果
        "ok": False,
        "sql": None,
        "preview": [],
        "attempts": 0,
        "error": None,
        "error_type": None,
    }
    for attempt in range(1, MAX_SQL_FIX + 2):  #第一次开始加上修复次数
        user = question + "\n\n列清单：\n" + columns   #user用来构造提示词
        if feedback:  #上一轮有错误的话就加载提示词后面
            user += "\n\n上一轮的错误：\n" + feedback
        reply = chat_fn(  #调用模型
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            model=MODEL,
        )
        sql = extract_sql(reply["content"])  #把模型回复的sql语句扣出来
        guarded = check_sql(sql, schema)  #门卫检查sql语句正确性
        last = {   #兜底返回结果，先认为sql语句不正确，如果后面判断正确的话会改
            "ok": False,
            "sql": sql,
            "preview": [],
            "attempts": attempt,
            "error": guarded.reason,
            "error_type": "guard",
        }
        if not guarded.ok:     #如果门卫检查不通过，得到原因开始开始下一轮，下一轮开头会把feedback进行拼接
            feedback = f"{guarded.reason}\nSQL:\n{sql}"
            continue
        result = run_fn(guarded.sql, schema=schema)  #执行的是门卫通过的sql语句，真的sql查询
        last = {  #兜底返回结果，如果查询成功的话会改
            "ok": result["ok"] and result["error_type"] != "empty",
            "sql": guarded.sql,
            "preview": result["preview"],
            "attempts": attempt,
            "error": result["error"],
            "error_type": result["error_type"],
        }
        if last["ok"]:  #如果查询成功的话就返回结果
            return last
        feedback = result["error"] or "query returned no rows"  #如果查询失败的话，把错误信息拼接起来
    return last

if __name__ == "__main__":
    from src.db.executor import run_sql
    from src.llm_client import chat
    print(run_question("orders 表一共有多少行？", chat_fn=chat, run_fn=run_sql, columns=COLUMNS))
