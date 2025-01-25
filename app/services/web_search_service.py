from app.services.openai_service import OpenAIService
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv
from app.prompts.ask_domains_prompt import ask_domains_prompt
import json
import asyncio
import os

load_dotenv(find_dotenv())


class WebSearchService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.allowed_domains = [
            {"name": "Wikipedia", "url": "wikipedia.org", "scrappable": True},
            {"name": "easycart", "url": "easy.tools", "scrappable": True},
            {"name": "FS.blog", "url": "fs.blog", "scrappable": True},
            {"name": "arXiv", "url": "arxiv.org", "scrappable": True},
            {"name": "Instagram", "url": "instagram.com", "scrappable": False},
            {"name": "OpenAI", "url": "openai.com", "scrappable": True},
            {"name": "Brain overment", "url": "brain.overment.com", "scrappable": True},
            {"name": "Reuters", "url": "reuters.com", "scrappable": True},
            {
                "name": "MIT Technology Review",
                "url": "technologyreview.com",
                "scrappable": True,
            },
            {"name": "Youtube", "url": "youtube.com", "scrappable": False},
            {"name": "Mrugalski / UWteam", "url": "mrugalski.pl", "scrappable": True},
            {"name": "overment", "url": "brain.overment.com", "scrappable": True},
            {"name": "Tailwind CSS", "url": "tailwindcss.com", "scrappable": True},
            {"name": "IMDB", "url": "imdb.com", "scrappable": True},
            {"name": "TechCrunch", "url": "techcrunch.com", "scrappable": True},
            {"name": "Hacker", "url": "news.ycombinator.com", "scrappable": True},
            {"name": "TechCrunch", "url": "techcrunch.com", "scrappable": True},
            {"name": "OpenAI", "url": "openai.com", "scrappable": True},
            {"name": "Anthropic", "url": "anthropic.com", "scrappable": True},
            {"name": "DeepMind Press", "url": "deepmind.google", "scrappable": True},
        ]
        self.api_key = os.getenv("FIRECRAWL_API_KEY", "")
        # self.firecrawl_app = FirecrawlApp({"apiKey": self.api_key})

    async def search(self, query: str, conversation_uuid: str) -> Dict[str, Any]:
        messages = [{"role": "user", "content": query}]

        queries = (await self.generate_queries(messages))["queries"]

        print(
            [
                {"Query Number": index + 1, "Query": query}
                for index, query in enumerate(queries)
            ]
        )

        docs = []

        if len(queries) > 0:
            search_results = await self.search_web(queries, conversation_uuid)
            print(
                "searchResults",
                [
                    [item["title"] + " " + item["url"] for item in r["results"]]
                    for r in search_results
                ],
            )
            resources = await self.select_resources_to_load(messages, search_results)
            scraped_content = await self.scrape_urls(resources, conversation_uuid)

            docs = await asyncio.gather(
                *[
                    self._create_document(
                        result, search_result, scraped_content, conversation_uuid
                    )
                    for search_result in search_results
                    for result in search_result["results"]
                ]
            )

        return docs

    async def generate_queries(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        system_prompt = {
            "role": "system",
            "content": ask_domains_prompt(self.allowed_domains),
        }

        try:
            response = await self.openai_service.completion(
                {
                    "messages": [system_prompt] + messages,
                    "model": "gpt-4o",
                    "jsonMode": True,
                }
            )

            result = json.loads(response.choices[0].message.content)
            print("result", result)
            filtered_queries = [
                query
                for query in result["queries"]
                if any(domain["url"] in query["url"] for domain in self.allowed_domains)
            ]
            return {"queries": filtered_queries, "thoughts": result["_thoughts"]}

        except Exception as error:
            print("Error generating queries:", error)
            return {"queries": [], "thoughts": ""}
