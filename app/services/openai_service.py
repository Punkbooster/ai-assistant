from openai import OpenAI
from typing import Dict, Any


class OpenAIService:
    def __init__(self):
        self.client = OpenAI()

    async def completion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        messages = config.get("messages")
        model = config.get("model", "gpt-4o-mini")
        stream = config.get("stream", False)
        json_mode = config.get("jsonMode", False)

        response_format = {"type": "json_object"} if json_mode else {"type": "text"}

        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            stream=stream,
            response_format=response_format,
        )
