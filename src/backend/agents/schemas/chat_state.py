from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class ChatState(TypedDict):
    """State for chat workflow"""
    
    # Input
    chat_id: int
    question: str
    chat_history: Optional[List[Dict[str, str]]]
    
    # Retrieved context
    retrieved_docs: Optional[List[Dict[str, Any]]]
    context: Optional[str]
    sources: Optional[List[str]]
    
    # Response
    response: Optional[str]
    
    # Metadata
    has_documents: bool
    needs_retrieval: bool
    