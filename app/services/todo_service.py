from app.services.openai_service import OpenAIService
from typing import List, Dict, Any
from msgraph import GraphServiceClient
from msgraph.generated.models.todo_task import TodoTask
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class TodoService:
    def __init__(self):
        scopes = ["https://graph.microsoft.com/.default"]

        # Values from app registration
        tenant_id = "f8cdef31-a31e-4b4a-93e4-5f571e91255a"
        client_id = "YOUR_CLIENT_ID"
        client_secret = "YOUR_CLIENT_SECRET"

        # azure.identity.aio
        credential = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )

        self.openai_service = OpenAIService()
        self.graph_client = GraphServiceClient(credential, scopes)

    async def create_task(self, title: str, category: str) -> str:
        request_body = TodoTask(
            title=title,
            categories=[
                category,
            ],
        )

        result = await self.graph_client.me.todo.lists.by_todo_task_list_id(
            "todoTaskList-id"
        ).tasks.post(request_body)

        return result
