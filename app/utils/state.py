import uuid
import json
from app.prompts.web_prompt import web_prompt

state = {
    "config": {"max_steps": 1, "current_step": 0, "active_step": None},
    "messages": [],
    "conversation_uuid": str(uuid.uuid4()),
    "tools": [
        {
            "uuid": str(uuid.uuid4()),
            "name": "web_search",
            "description": "Use this to search the web for external information",
            "instruction": web_prompt(),
            "parameters": json.dumps(
                {
                    "query": "Command to the web search tool, including the search query and all important details, keywords and urls from the available context"
                }
            ),
        },
        {
            "uuid": str(uuid.uuid4()),
            "name": "final_answer",
            "description": "Use this tool to write a message to the user",
            "instruction": "...",
            "parameters": json.dumps({}),
        },
        {
            "uuid": str(uuid.uuid4()),
            "name": "mailer",
            "description": "Use this tool to send an email to a specified address",
            "instruction": "...",
            "parameters": json.dumps(
                {
                    "title": "The subject line of the email",
                    "content": "The body content of the email",
                    "address": "The recipient's email address",
                }
            ),
        },
    ],
    "documents": [],
    "actions": [],
}
