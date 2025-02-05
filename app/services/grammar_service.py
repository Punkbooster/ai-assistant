from fastapi import HTTPException, status
from app.prompts.grammar_prompt import GRAMMAR_PROMPT

async def fix_grammar(ChatService, question_content: str) -> str:
    try:
        all_messages = [
            {"role": "system", "content": GRAMMAR_PROMPT, "name": "Assistant"},
            {"role": "user", "content": question_content},
        ]

        main_completion = await ChatService.completion(all_messages, "gpt-4o-mini")

        main_message = main_completion.choices[0].message.content

        return main_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
