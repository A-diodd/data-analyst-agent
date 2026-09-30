#把用户随口说的指标名，转换成yaml文件里面定义好的那个指标对象
from difflib import get_close_matches  #用户会打错字，这里能模糊匹配
from pathlib import Path

import yaml


METRICS_PATH = Path(__file__).resolve().parents[1] / "semantic" / "metrics.yaml"

#经过安全导入，把yaml文件里面的指标弄成字典列表
def load_metrics() -> list[dict]:
    return yaml.safe_load(METRICS_PATH.read_text(encoding="utf-8"))

#把指标所有可能的叫法全部放进列表里面
def _labels(metric: dict) -> list[str]:
    labels = [metric["name"], metric.get("zh") or ""]
    labels.extend(metric.get("aliases") or [])
    return [label for label in labels if label]

def get_metric_definition(name_or_alias: str) -> dict | None:
    needle = name_or_alias.strip()
    if not needle:
        return None
    metrics = load_metrics()
    lowered = needle.lower()
    for metric in metrics:
        if any(label.lower() == lowered for label in _labels(metric)):
            return metric   #到这里是精准匹配
    by_label = {label: metric for metric in metrics for label in _labels(metric)}
    found = get_close_matches(needle, list(by_label), n=1, cutoff=0.6)
    if not found:
        return None
    return by_label[found[0]]  #到这里是模糊匹配

'''
by_label大概长这样
by_label = {
    "gmv": {...gmv 的完整定义...},
    "成交总额": {...gmv 的完整定义...},
    "GMV": {...gmv 的完整定义...},
    "销售额": {...gmv 的完整定义...},
    "成交额": {...gmv 的完整定义...},
    "order_count": {...order_count 的定义...},
    ...
}
... 
'''
#把用户提到的问题里面的指标，按照指标的定义拼成一段文字返回
def definitions_for_question(question: str) -> str:
    labels = []
    for metric in load_metrics():
        for label in _labels(metric):
            labels.append((label,metric))  #把叫法，指标定义成元组列表
    labels.sort(key=lambda item: len(item[0]),reverse = True) #reverse降序排列
    #labels包含了所有指标的名字和别名

    found = []  #用来放命中的指标列表
    seen= set() #用来放已经处理过的指标名字
    lowered = question.lower()  #把问题转换成小写
    for label,metric in labels:  #把二元组拆开
        if metric["name"] in seen:
            continue
        if label.lower() not in lowered:
            continue
        seen.add(metric["name"])
        found.append(metric)
    lines = []
    for metric in found:
        line = f"{metric.get('zh') or metric['name']}：{metric['definition']}"
        if metric.get("numerator") and metric.get("denominator"):
            line += f"。分子是{metric['numerator']}，分母是{metric['denominator']}"
        lines.append(line)
    return "\n".join(lines)

