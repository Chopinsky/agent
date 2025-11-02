import os
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

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
        # Some OpenAI client builds may not accept `api_key` in the constructor
        # (or may pass unexpected kwargs). To be robust, set the environment
        # variable and instantiate the client without kwargs.
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key

        try:
            self._client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.exception("OpenAIClient not configured properly: %s", e)
            self._client = None

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
        choice = resp.choices[0]
        if choice.finish_reason == "function_call" and choice.message is not None:
            fc = choice.message.function_call
            name = fc.name
            args_text = fc.arguments or "{}"

            try:
                args = json.loads(args_text)
            except Exception:
                # sometimes arguments are already a dict
                args = args_text

            return {"name": name, "arguments": args}
    except Exception as e:
        logger.exception("Error extracting function call: %s", e)

    return None


__all__ = ["OpenAIClient", "extract_function_call"]
