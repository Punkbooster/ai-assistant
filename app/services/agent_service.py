import uuid
import json
from app.services.openai_service import OpenAIService
from app.services.web_search_service import WebSearchService
from app.services.mailer_service import MailerService
from app.prompts.answer_prompt import answer_prompt
from app.prompts.generate_params_prompt import generate_params_prompt
from app.prompts.create_plan_prompt import create_plan_prompt


class Agent:
    def __init__(self, state):
        self.openai_service = OpenAIService()
        self.web_search_service = WebSearchService(state["conversation_uuid"])
        self.mailer_service = MailerService()
        self.state = state

    async def process_agent_steps(self, state):
        for i in range(state["config"]["max_steps"]):
            # Make a plan
            next_move = await self.plan()
            print("Thinking...", next_move["_reasoning"])
            print(f"Selected Tool: {next_move['tool']}, Query: {next_move['query']}")

            # If there's no tool to use, we're done
            if not next_move["tool"] or next_move["tool"] == "final_answer":
                break

            # Set the active step
            state["config"]["active_step"] = {
                "name": next_move["tool"],
                "query": next_move["query"],
            }

            # Generate the parameters for the tool
            parameters = await self.describe(next_move["tool"], next_move["query"])

            # Use the tool
            await self.use_tool(next_move["tool"], parameters)

            # Increase the step counter
            state["config"]["current_step"] += 1

        # Generate the final answer
        answer = await self.generate_answer()
        state["messages"].append(answer.choices[0].message.content)

        return state["messages"][-1]

    async def plan(self):
        system_message = create_plan_prompt(self.state)

        answer = await self.openai_service.completion(
            {
                "messages": [system_message],
                "model": "gpt-4o",
                "stream": False,
                "jsonMode": True,
                "conversation_uuid": self.state["conversation_uuid"],
            }
        )

        result = json.loads(answer.choices[0].message.content or "{}")
        return result if "tool" in result else None

    async def describe(self, tool, query):
        tool_info = next((t for t in self.state["tools"] if t["name"] == tool), None)

        if not tool_info:
            raise ValueError(f"Tool {tool} not found")

        system_message = generate_params_prompt(self.state, tool_info, query)

        answer = await self.openai_service.completion(
            {
                "messages": [system_message],
                "model": "gpt-4o",
                "stream": False,
                "jsonMode": True,
                "conversation_uuid": self.state["conversation_uuid"],
            }
        )

        return json.loads(answer.choices[0].message.content or "{}")

    async def use_tool(self, tool, parameters):
        if tool == "web_search":
            results = await self.web_search_service.search(parameters["query"])

            self.state["documents"].extend(
                [r for r in results if r["metadata"]["content_type"] != "chunk"]
            )
            self.state["actions"].append(
                {
                    "uuid": str(uuid.uuid4()),
                    "name": tool,
                    "parameters": json.dumps(parameters),
                    "description": f'Search results & website contents for the query {parameters["query"]}',
                    "results": results,
                    "tool_uuid": tool,
                }
            )
        elif tool == "mailer":
            is_success, result_message = await self.mailer_service.send(
                recipient_email=parameters["address"], subject=parameters["title"], content=parameters["content"]
            )

            if is_success == True:
                self.state["actions"].append(
                    {
                        "uuid": str(uuid.uuid4()),
                        "name": tool,
                        "parameters": json.dumps(parameters),
                        "description": f'Sent email to {parameters["address"]} with the subject {parameters["title"]}',
                        "results": result_message,
                        "tool_uuid": tool,
                    }
                )
            else:
                self.state["actions"].append(
                    {
                        "uuid": str(uuid.uuid4()),
                        "name": tool,
                        "parameters": json.dumps(parameters),
                        "description": f'Failed to send an email to {parameters["address"]} with the subject {parameters["title"]}',
                        "results": result_message,
                        "tool_uuid": tool,
                    }
                )

    async def generate_answer(self):
        context = []

        for action in self.state["actions"]:
            for result in action["results"]:
                context.append(result)

        query = (
            self.state["config"]["active_step"]["query"]
            if self.state["config"]["active_step"]
            else None
        )

        answer = await self.openai_service.completion(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": answer_prompt(context, query),
                    },
                    *self.state["messages"],
                ],
                "model": "gpt-4o-mini",
                "stream": False,
                "conversation_uuid": self.state["conversation_uuid"],
            }
        )

        return answer
