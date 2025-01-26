import uuid
from typing import Dict, Any

def generate_metadata(params: Dict[str, Any]) -> Dict[str, Any]:
    """
        Generates standardized metadata for documents.

        :param params: Parameters to include in the metadata.
        :return: A standardized metadata object.
    """
    return {
        "uuid": str(uuid.uuid4()),
        "source_uuid": str(uuid.uuid4()),
        "conversation_uuid": params.get("conversation_uuid", ""),
        "source": params["source"],
        "name": params["name"],
        "mimeType": params["mimeType"],
        "description": params.get("description"),
        **params.get("additional", {}),
    }
