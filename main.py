from fastapi.security import HTTPAuthorizationCredentials
from app.services.chat_service import ChatService
from app.utils.auth_utils import verify_token
from pydantic import BaseModel
from app.services.agent_service import Agent
from app.utils.state import state as State
from app.services.grammar_service import fix_grammar
from langfuse import Langfuse
from fastapi import FastAPI, Depends, HTTPException, status
import uuid


class Question(BaseModel):
    content: str


app = FastAPI()
ChatService = ChatService()
langfuse = Langfuse()


@app.post("/answer")
async def get_answer(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        state = State
        state["messages"].append({"role": "user", "content": question.content})

        agent = Agent(state)

        final_answer = await agent.process_agent_steps(state)

        return final_answer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/grammar")
async def grammar(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        final_answer = await fix_grammar(ChatService, question.content)

        return final_answer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
