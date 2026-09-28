
import json
from datetime import datetime,timezone
from pathlib import Path

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" #取到运行时的目录

def write_trace(
    task_id:str,
    *,    #这后面的参数必须按关键字传入
    node,
    event:str,
    latency_ms:int | None = None,
    prompt_tokens:int | None = None,
    completion_tokens:int | None = None,
    tool: str|None = None,
    ok:bool | None = None,
    error_type:str | None = None,
    cache_hit:bool | None = None,
    detail:str | None = None,
) -> None:
    RUNS_DIR.mkdir(parents=True,exist_ok=True)
    record = {
        "task_id":task_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "node":node,
        "event": event,
        "latency_ms":latency_ms,
        "prompt_tokens":prompt_tokens,
        "completion_tokens":completion_tokens,
        "tool":tool,
        "ok":ok,
        "error_type":error_type,
        "cache_hit":cache_hit,
        "detail":detail,
    }
    path = RUNS_DIR / f"{task_id}.jsonl"
    with path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(record,ensure_ascii=False) + "\n")
