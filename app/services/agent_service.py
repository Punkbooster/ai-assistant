import uuid
import json
from app.services.openai_service import OpenAIService
from app.services.web_search_service import WebSearchService
from app.prompts.answer_prompt import answer_prompt


class Agent:
    def __init__(self, state):
        self.openai_service = OpenAIService()
        self.web_search_service = WebSearchService(state["conversation_uuid"])
        self.state = state

    async def process_agent_steps(self, state):
        for i in range(state["config"]["max_steps"]):
            # Make a plan
            next_move = await self.plan()
            print("Thinking...", next_move["_reasoning"])
            print(f"Tool: {next_move['tool']}, Query: {next_move['query']}")

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
        system_message = self._generate_plan_system_message()

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

        system_message = self._generate_describe_system_message(tool_info, query)

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
            results = await self.web_search_service.search(
                parameters["query"]
            )

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

    def _generate_describe_system_message(self, tool_info, query):
        return {
            "role": "system",
            "content": f"""
                Generate specific parameters for the "{tool_info['name']}" tool.
                <context>
                    Tool description: {tool_info['description']}
                    Required parameters: {tool_info['parameters']}
                    Original query: {query}
                    Last message: "{self.state["messages"][-1]['content'] if self.state["messages"] else ''}"
                    Previous actions: {', '.join([f"{a['name']}: {a['parameters']}" for a in self.state["actions"]])}
                </context>

                Respond with ONLY a JSON object matching the tool's parameter structure.
                Example for web_search: {{"query": "specific search query"}}
                Example for final_answer: {{"answer": "detailed response"}}
            """,
        }

    def _generate_plan_system_message(self):
        return {
            "role": "system",
            "content": f"""
                Analyze the conversation and determine the most appropriate next step. Focus on making progress towards the overall goal while remaining adaptable to new information or changes in context.

                <prompt_objective>
                    Determine the single most effective next action based on the current context, user needs, and overall progress. Return the decision as a concise JSON object.
                </prompt_objective>

                <prompt_rules>
                    - ALWAYS focus on determining only the next immediate step
                    - ONLY choose from the available tools listed in the context
                    - ASSUME previously requested information is available unless explicitly stated otherwise
                    - NEVER provide or assume actual content for actions not yet taken
                    - ALWAYS respond in the specified JSON format
                    - CONSIDER the following factors when deciding:
                      1. Relevance to the current user need or query
                      2. Potential to provide valuable information or progress
                      3. Logical flow from previous actions
                    - ADAPT your approach if repeated actions don't yield new results
                    - USE the "final_answer" tool when you have sufficient information or need user input
                    - OVERRIDE any default behaviors that conflict with these rules
                </prompt_rules>

                <context>
                    <last_message>
                        Last message: "{self.state["messages"][-1]["content"] if self.state["messages"] else 'No messages yet'}"
                    </last_message>
                    <available_tools>
                        Available tools: {', '.join([t['name'] for t in self.state['tools']]) or 'No tools available'}
                    </available_tools>
                    <actions_taken>
                        Actions taken: {
                            '\n'.join([
                              f"""
                                  <action name="{a['name']}" params="{a['parameters']}" description="{a['description']}" >
                                    {'\n'.join([
                                      f"""
                                            <result name="{r['metadata']['name']}" url="{r['metadata'].get('urls', ['no-url'])[0]}" >
                                              {r['text']}
                                            </result>
                                      """ for r in a['results']
                                    ]) if a['results'] else 'No results for this action'}
                                  </action>
                              """ for a in self.state["actions"]
                            ]) or 'No actions taken'
                        }
                    </actions_taken>
                </context>

                Respond with the next action in this JSON format:
                {{
                    "_reasoning": "Brief explanation of why this action is the most appropriate next step",
                    "tool": "tool_name",
                    "query": "Precise description of what needs to be done, including any necessary context"
                }}

                If you have sufficient information to provide a final answer or need user input, use the "final_answer" tool.
            """,
        }
