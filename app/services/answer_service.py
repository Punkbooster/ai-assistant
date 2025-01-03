from openai import OpenAI
from app.prompts import GRAMMA_PROMPT

def get_answer(content: str, openai_client: OpenAI):
    result = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            { "role": "system", "content": GRAMMA_PROMPT },
            { "role": "user", "content": content }
        ]
    )

    return result.choices[0].message.content
