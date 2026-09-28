import os
import time 

from dotenv import load_dotenv
from openai import OpenAI

def create_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is not set")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

def chat(messages, *, model=None, json_mode=False, temperature=0) -> dict:
    if not messages:
        raise ValueError("messages is 不能为空")
    
    kwargs = {
        "model": model or "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    
    started = time.perf_counter()
    response = create_client().chat.completions.create(**kwargs)
    latency_ms = int((time.perf_counter() - started) * 1000) #算回复延时

    usage = response.usage
    return {
        "content": response.choices[0].message.content or "",
        "usage": {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
        },
        "latency_ms": latency_ms,
        "cached":False,
    }