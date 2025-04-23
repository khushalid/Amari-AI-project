import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TODO: Add configuration options

    # OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Form URL
    FORM_URL: str = "https://docs.google.com/forms/d/e/1FAIpQLSemlBSMvQsQZnAudDXMWXGldJGdZW6VkoDAwbQKsuTGlgZfNg/viewform"
    
    # Document types
    ALLOWED_DOCUMENT_TYPES: list[str] = [".pdf", ".xlsx"]

settings = Settings()
