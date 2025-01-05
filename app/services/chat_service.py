from app.services.openai_service import OpenAIService
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class ChatService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def completion(
        self, messages: List[Dict[str, Any]], model: str
    ) -> Dict[str, Any]:
        params = {
            "messages": messages,
            "model": model,
            "stream": False,
            "json_mode": False,
        }

        return await self.openai_service.completion(params)
