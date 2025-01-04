from app.prompts import GRAMMA_PROMPT
from openai import OpenAI


async def generate_completion(content: str, openai_client: OpenAI):
    result = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GRAMMA_PROMPT},
            {"role": "user", "content": content},
        ],
    )

    return result.choices[0].message.content
