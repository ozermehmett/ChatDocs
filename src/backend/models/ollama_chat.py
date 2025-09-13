import requests
import logging
from typing import List, Dict
from .base_chat import BaseChatModel
from config import settings

logger = logging.getLogger(__name__)

class OllamaChat(BaseChatModel):
    """Ollama chat model implementation"""
    
    def __init__(self, model_name: str = None):
        super().__init__(model_name or settings.OLLAMA_MODEL)
        self.base_url = settings.OLLAMA_BASE_URL
        self.session = requests.Session()
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Ollama API"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
        except KeyError as e:
            logger.error(f"Unexpected Ollama API response format: {str(e)}")
            raise Exception(f"Invalid response from Ollama: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=20)
            response.raise_for_status()
            
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except:
            logger.error("Failed to list Ollama models")
            return []

# Global instance
ollama_chat = OllamaChat()
