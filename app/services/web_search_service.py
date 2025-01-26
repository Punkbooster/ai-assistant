from app.services.openai_service import OpenAIService
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv
from app.prompts.ask_domains_prompt import ask_domains_prompt
from app.prompts.pick_resources_prompt import pick_resources_prompt
from firecrawl import FirecrawlApp
from app.services.text_service import TextService
from urllib.parse import urlparse
import json
import asyncio
import os
import aiohttp
import uuid

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
            {"name": "overment", "url": "brain.overment.com", "scrappable": True},
            {"name": "Tailwind CSS", "url": "tailwindcss.com", "scrappable": True},
            {"name": "IMDB", "url": "imdb.com", "scrappable": True},
            {"name": "TechCrunch", "url": "techcrunch.com", "scrappable": True},
            {"name": "Hacker", "url": "news.ycombinator.com", "scrappable": True},
            {"name": "Anthropic", "url": "anthropic.com", "scrappable": True},
            {"name": "DeepMind Press", "url": "deepmind.google", "scrappable": True},
        ]
        self.api_key = os.getenv("FIRECRAWL_API_KEY", "")
        self.firecrawl_app = FirecrawlApp(api_key=self.api_key)
        self.text_service = TextService()


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
            search_results = await self.search_web(queries)
            print(
                "searchResults",
                [
                    [item["title"] + " " + item["url"] for item in r["results"]]
                    for r in search_results
                ],
            )
            resources = await self.select_resources_to_load(messages, search_results)
            scraped_content = await self.scrape_urls(resources)

            docs = []

            for search_result in search_results:
                for result in search_result["results"]:
                    normalized_result_url = result["url"].rstrip('/')

                    # match the scraped content with the search result
                    scraped_item = next((item for item in scraped_content if item["url"].rstrip('/') == normalized_result_url), None)
                    content = scraped_item["content"] if scraped_item else result["description"]

                    doc = self.text_service.document(
                        content,
                        'gpt-4o',
                        {
                            "name": result["title"],
                            "description": f'This is a result of a web search for the query: "{search_result["query"]}"',
                            "source": result["url"],
                            "content_type": 'complete' if scraped_item else 'chunk',
                            "uuid": str(uuid.uuid4()),
                            "conversation_uuid": conversation_uuid,
                        }
                    )
                    docs.append(doc)
            docs = await asyncio.gather(*docs)

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
            print("\n\nresult", result)
            filtered_queries = [
                query
                for query in result["queries"]
                if any(domain["url"] in query["url"] for domain in self.allowed_domains)
            ]
            return {"queries": filtered_queries, "thoughts": result["_thoughts"]}

        except Exception as error:
            print("Error generating queries:", error)
            return {"queries": [], "thoughts": ""}

    async def search_web(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = []

            for query in queries:
                tasks.append(
                    self._search_single_query(session, query["q"], query["url"])
                )

            search_results = await asyncio.gather(*tasks)

        return search_results

    async def _search_single_query(self, session, q: str, url: str) -> Dict[str, Any]:
        try:
            # Add site: prefix to the query using domain
            domain = url if url.startswith("https://") else f"https://{url}"
            domain = domain.rstrip("/")
            site_query = f"site:{domain} {q}"
            async with session.post(
                "https://api.firecrawl.dev/v1/search",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                data=json.dumps({"query": site_query, "limit": 3}),
            ) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error! status: {response.status}")

                result = await response.json()

                if (
                    result.get("success")
                    and result.get("data")
                    and isinstance(result["data"], list)
                ):
                    return {
                        "query": q,
                        "domain": domain,
                        "results": [
                            {
                                "url": item["url"],
                                "title": item["title"],
                                "description": item["description"],
                            }
                            for item in result["data"]
                        ],
                    }
                else:
                    print(f'No results found for query: "{site_query}"')
                    return {"query": q, "domain": domain, "results": []}
        except Exception as error:
            print(f'Error searching for "{q}":', error)
            return {"query": q, "domain": url, "results": []}

    async def select_resources_to_load(
        self, messages: List[Dict[str, Any]], filtered_results: List[Dict[str, Any]]
    ) -> List[str]:
        system_prompt = {
            "role": "system",
            "content": pick_resources_prompt(filtered_results),
        }

        try:
            response = await self.openai_service.completion(
                {
                    "messages": [system_prompt] + messages,
                    "model": "gpt-4o",
                    "jsonMode": True,
                }
            )

            if response.choices[0].message.content:
                result = json.loads(response.choices[0].message.content)
                selected_urls = result["urls"]

                print("\n\nselectedUrls", selected_urls)
                # Filter out URLs that aren't in the filtered results
                valid_urls = [
                    url
                    for url in selected_urls
                    if any(
                        r["results"]
                        for r in filtered_results
                        if any(item["url"] == url for item in r["results"])
                    )
                ]

                # Get domains with empty results
                empty_domains = [
                    r["domain"] for r in filtered_results if len(r["results"]) == 0
                ]

                # Combine valid_urls and empty_domains
                combined_urls = valid_urls + empty_domains

                return combined_urls

            raise Exception("Unexpected response format")
        except Exception as error:
            print("Error selecting resources to load:", error)
            return []

    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        print("\n\nInput (scrapeUrls):", urls)

        # Filter out URLs that are not scrappable based on allowedDomains
        scrappable_urls = []
        for url in urls:
            domain = urlparse(url).hostname.replace("www.", "")
            for d in self.allowed_domains:
                if d["url"] == domain and d["scrappable"]:
                    scrappable_urls.append(url)
                    break

        scrape_promises = [self.scrape_url(url) for url in scrappable_urls]
        scraped_results = await asyncio.gather(*scrape_promises)

        return [result for result in scraped_results if result["content"]]

    async def scrape_url(self, url):
        try:
            url = url.rstrip("/")
            scrape_result = self.firecrawl_app.scrape_url(
                url, {"formats": ["markdown"]}
            )

            if scrape_result and scrape_result.get("markdown"):
                return {"url": url, "content": scrape_result["markdown"].strip()}
            else:
                print(f"No markdown content found for URL: {url}")

                return {"url": url, "content": ""}
        except Exception as error:
            print(f"Error scraping URL {url}:", error)

            return {"url": url, "content": ""}
