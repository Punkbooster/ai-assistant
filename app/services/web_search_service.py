from app.services.openai_service import OpenAIService
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class WebSearchService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def search(self, query: str, model: str) -> Dict[str, Any]:
        return await "to be implemented"
