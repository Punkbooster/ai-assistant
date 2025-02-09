from typing import Dict, Any
from langfuse.openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI()

    async def completion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        messages = config.get("messages")
        model = config.get("model", "gpt-4o-mini")
        stream = config.get("stream", False)
        json_mode = config.get("jsonMode", False)
        temperature = config.get("temperature", 0.2)
        session_id = config.get("conversation_uuid")

        response_format = {"type": "json_object"} if json_mode else {"type": "text"}

        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            stream=stream,
            response_format=response_format,
            temperature=temperature,
            session_id=session_id,
        )
