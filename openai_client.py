import os
import json
from typing import Any, Dict, List, Optional

import openai

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    # allow the app to raise later when an operation requires the key
    pass
else:
    openai.api_key = OPENAI_KEY


def call_chat_completion(messages: List[Dict[str, Any]], functions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Call OpenAI chat completion with function calling enabled (auto).

    This function returns the raw response. The server will handle function call execution.
    """
    if OPENAI_KEY is None:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")

    kwargs: Dict[str, Any] = {
        "model": "gpt-4o-mini",
        # "gpt-4o-mini" is used as an example; change if needed.
        "messages": messages,
        "temperature": 0.2,
    }
    if functions:
        kwargs["functions"] = functions
        kwargs["function_call"] = "auto"

    resp = openai.ChatCompletion.create(**kwargs)
    return resp


def extract_function_call(resp: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """If the model returned a function_call, return its name and arguments (parsed JSON)."""
    try:
        choice = resp["choices"][0]
        message = choice.get("message", {})
        if message.get("function_call"):
            fc = message["function_call"]
            name = fc.get("name")
            args_text = fc.get("arguments") or "{}"
            try:
                args = json.loads(args_text)
            except Exception:
                # sometimes arguments are already a dict
                args = args_text
            return {"name": name, "arguments": args}
    except Exception:
        pass
    return None


__all__ = ["call_chat_completion", "extract_function_call"]
