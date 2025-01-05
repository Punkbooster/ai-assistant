from fastapi.security import HTTPAuthorizationCredentials
from app.services.chat_service import ChatService
from app.utils.auth_utils import verify_token
from pydantic import BaseModel
from prompts import GRAMMAR_PROMPT
from fastapi import FastAPI, Depends, HTTPException, status


class Question(BaseModel):
    content: str


app = FastAPI()
ChatService = ChatService()


@app.post("/answer")
async def get_answer(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        content = question.content

        all_messages = [
            {"role": "system", "content": GRAMMAR_PROMPT, "name": "Assistant"},
            {"role": "user", "content": content, "name": "Arsen"},
        ]

        main_completion = await ChatService.completion(all_messages, "gpt-4o-mini")

        main_message = main_completion.choices[0].message.content

        return main_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
