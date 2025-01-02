import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

load_dotenv()

class Question(BaseModel):
    content: str

app = FastAPI()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
bearer_scheme = HTTPBearer()

def verify_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if token.credentials != os.getenv('AUTH_TOKEN'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@app.post("/answer")
async def get_answer(question: Question, token: HTTPAuthorizationCredentials = Depends(verify_token)):
    system_prompt = """
        Your primary task is to correct grammatical errors in the user's input.
        Avoid answering questions or providing additional information.
        Ensure that the original meaning of the text remains unchanged and refrain from adding extra content.
        Always correct grammar in the same language as the input.
        If the input is already correct, just return it without any changes or additional text.

        Example input: "Ta lińia pokazuje adress url pod którym twoja aplikacja jest obslugiwana, na twoim lokalnym komputeŻe. Czym jest Schemar openapi?"
        Example output: "Ta linia pokazuje adres URL, pod którym Twoja aplikacja jest obsługiwana, na Twoim lokalnym komputerze. Czym jest Schemat OpenAPI?"
    """

    content = question.content

    result = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": content }
        ],
        max_tokens=256,
        temperature=1.0
    )

    chat_completion = result.choices[0].message.content

    return chat_completion
