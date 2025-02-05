from fastapi.security import HTTPAuthorizationCredentials
from app.services.chat_service import ChatService
from app.utils.auth_utils import verify_token
from pydantic import BaseModel
from app.services.agent_service import Agent
from app.utils.state import state as State
from app.prompts.grammar_prompt import GRAMMAR_PROMPT
from fastapi import FastAPI, Depends, HTTPException, status
import uuid


class Question(BaseModel):
    content: str


app = FastAPI()
ChatService = ChatService()


@app.post("/answer")
async def get_answer(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        conversation_uuid = uuid.uuid4()
        state = State
        state["messages"].append({"role": "user", "content": question.content})

        agent = Agent(state)

        for i in range(state["config"]["max_steps"]):
            # Make a plan
            next_move = await agent.plan()
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
            parameters = await agent.describe(next_move["tool"], next_move["query"])

            # Use the tool
            await agent.use_tool(next_move["tool"], parameters, conversation_uuid)

            # Increase the step counter
            state["config"]["current_step"] += 1

        # Generate the final answer
        answer = await agent.generate_answer()
        state["messages"].append(answer.choices[0].message.content)

        return state["messages"][-1]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@app.post("/grammar")
async def fix_grammar(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        content = question.content

        all_messages = [
            {"role": "system", "content": GRAMMAR_PROMPT, "name": "Assistant"},
            {"role": "user", "content": content},
        ]

        main_completion = await ChatService.completion(all_messages, "gpt-4o-mini")

        main_message = main_completion.choices[0].message.content

        return main_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
