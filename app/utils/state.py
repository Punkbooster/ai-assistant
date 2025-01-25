import uuid
import json
from app.prompts.web_prompt import web_prompt

state = {
    "config": {"max_steps": 5, "current_step": 0, "active_step": None},
    "messages": [],
    "tools": [
        {
            "uuid": str(uuid.uuid4()),
            "name": "web_search",
            "description": "Use this to search the web for external information",
            "instruction": web_prompt,
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
    ],
    "documents": [],
    "actions": [],
}
