from openai import OpenAI  
from app.core.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def extract_fields_from_document(document_text, return_fields):
    """
    Extracts specified fields from document text using OpenAI's JSON schema mode.
    
    Args:
        document_text: Text content of the document
        return_fields: List of field names to extract (e.g., ["lease_term", "rent_amount"])
        
    Returns:
        dict: Extracted fields and their values
    """
    print("text", document_text)
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Extract specified fields from lease agreements. Return only the requested data in JSON format."
            },
            {
                "role": "user", 
                "content": f"Extract these fields: {', '.join(return_fields)} from:\n{document_text}"
            }
        ],
        response_format={
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {field: {"type": "string"} for field in return_fields},
                "required": return_fields,
                "additionalProperties": False
            }
        },
        temperature=0  # For consistent output
    )
    
    return json.loads(response.choices[0].message.content)