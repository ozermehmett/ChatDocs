import requests
import logging
from typing import List
from config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Client for custom embedding API service"""
    
    def __init__(self):
        self.base_url = settings.EMBEDDING_API_URL
        self.session = requests.Session()
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for list of texts"""
        try:
            response = self.session.post(
                f"{self.base_url}/embed",
                json={"text": texts},
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            return data["embeddings"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Embedding API request failed: {str(e)}")
            raise Exception(f"Failed to get embeddings: {str(e)}")
    
    def get_single_embedding(self, text: str) -> List[float]:
        """Get embedding for single text"""
        embeddings = self.get_embeddings([text])
        return embeddings[0]

# Global instance
embedding_service = EmbeddingService()
