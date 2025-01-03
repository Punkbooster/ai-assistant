from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.services.answer_service import get_answer
from app.utils.auth_utils import verify_token
from pydantic import BaseModel

load_dotenv()

class Question(BaseModel):
    content: str

app = FastAPI()
openai_client = OpenAI()

@app.post("/answer")
async def get_answer(question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)):
    content = question.content

    chat_completion = get_answer(content, openai_client)

    return chat_completion
