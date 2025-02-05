from app.services.openai_service import OpenAIService
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv
from app.utils.metadata import generate_metadata


class TextService:
    async def document(
        self,
        content: str,
        model_name: Optional[str] = None,
        metadata_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if metadata_overrides is None:
            metadata_overrides = {}

        base_metadata = generate_metadata(
            {
                "source": metadata_overrides.get("source", "generated"),
                "name": metadata_overrides.get("name", "Generated Document"),
                "mimeType": metadata_overrides.get("mimeType", "text/plain"),
                "conversation_uuid": metadata_overrides.get("conversation_uuid"),
                "additional": metadata_overrides.get("additional", {}),
            }
        )

        return {
            "text": content,
            "metadata": {
                **base_metadata,
                **metadata_overrides,
            },
        }
