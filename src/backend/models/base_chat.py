from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseChatModel(ABC):
    """Abstract base class for chat models"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if model is available"""
        pass
    
    def format_messages(self, system_prompt: str, user_message: str, chat_history: List[Dict] = None) -> List[Dict[str, str]]:
        """Format messages for the model"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    