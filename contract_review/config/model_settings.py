from enum import Enum
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"

class ModelSettings:
    """Configuration for LLM and embedding models."""
    
    @staticmethod
    def get_llm_provider() -> LLMProvider:
        """Get the LLM provider from environment variables."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        return LLMProvider(provider)
    
    @staticmethod
    def get_llm_model() -> str:
        """Get the model name based on provider."""
        provider = ModelSettings.get_llm_provider()
        if provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-4")
        else:
            return os.getenv("OLLAMA_MODEL", "llama3.2")
            
    @staticmethod
    def get_embedding_model() -> str:
        """Get the embedding model name."""
        return os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    @staticmethod
    def get_ollama_base_url() -> str:
        """Get Ollama base URL."""
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") 