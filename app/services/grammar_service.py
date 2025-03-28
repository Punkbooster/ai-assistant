import uuid
from fastapi import HTTPException, status
from app.prompts.grammar_prompt import grammar_prompt


async def fix_grammar(ChatService, question_content: str) -> str:
    try:
        all_messages = [
            {"role": "system", "content": grammar_prompt(), "name": "Assistant"},
            {"role": "user", "content": question_content},
        ]

        conversation_uuid = str(uuid.uuid4())

        main_completion = await ChatService.completion(all_messages, "gpt-4o-mini", conversation_uuid)

        main_message = main_completion.choices[0].message.content

        return main_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
