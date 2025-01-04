from dotenv import load_dotenv
from openai import OpenAI
from fastapi.security import HTTPAuthorizationCredentials
from app.services.completion_service import generate_completion
from app.utils.auth_utils import verify_token
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status

load_dotenv()
openai_client = OpenAI()


class Question(BaseModel):
    content: str


app = FastAPI()


@app.post("/answer")
async def get_answer(
    question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    try:
        content = question.content

        print(f"Received question: {content}")

        chat_completion = await generate_completion(content, openai_client)

        return chat_completion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
