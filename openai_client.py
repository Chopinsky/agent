import os
import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

# Default API key read from environment; can be overridden when constructing OpenAIClient
DEFAULT_OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


class OpenAIClient:
    """Wrapper around the OpenAI python client.

    Usage:
      client = OpenAIClient(api_key="sk-...")
      resp = client.call_chat_completion(messages, functions=[...])

    The constructor sets the API key used by openai. If no key is passed, the
    client will try to use the `OPENAI_API_KEY` environment variable.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", timeout: int = 60) -> None:
        self.api_key = api_key or DEFAULT_OPENAI_KEY
        self.model = model
        self.timeout = timeout

        # Create an OpenAI client instance from the new v1 interface.
        # Passing `api_key=None` is fine; the client will use environment vars
        # if available.
        self._client = OpenAI(api_key=self.api_key)

    def call_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = "auto",
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Call OpenAI ChatCompletion with optional function calling.

        Returns the raw API response (dict-like).
        """
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment or passed to OpenAIClient")

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if functions:
            kwargs["functions"] = functions
            # allow explicit override of function_call; default to auto when functions present
            kwargs["function_call"] = function_call or "auto"

        # Use the v1 client: client.chat.completions.create(...)
        resp = self._client.chat.completions.create(**kwargs)
        return resp


def extract_function_call(resp: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """If the model returned a function_call, return its name and parsed arguments.

    Returns {'name': <str>, 'arguments': <dict>} or None.
    """
    try:
        choice = resp["choices"][0]
        # Different OpenAI client versions place the message in different spots
        message = choice.get("message") or choice.get("delta") or {}
        if message and message.get("function_call"):
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


__all__ = ["OpenAIClient", "extract_function_call"]
