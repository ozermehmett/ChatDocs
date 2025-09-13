import logging
from typing import Dict, Any
from ..schemas.chat_state import ChatState
from ...services.vector_service import vector_service

logger = logging.getLogger(__name__)

def retrieve_documents(state: ChatState) -> Dict[str, Any]:
    """Retrieve relevant documents from vector store"""
    
    chat_id = state["chat_id"]
    question = state["question"]
    
    try:
        # Check if collection exists
        if not vector_service.collection_exists(chat_id):
            logger.info(f"No documents found for chat {chat_id}")
            return {
                "retrieved_docs": [],
                "context": "",
                "sources": [],
                "has_documents": False,
                "needs_retrieval": False
            }
        
        # Search for similar documents
        similar_docs = vector_service.search_similar(chat_id, question, n_results=5)
        
        if not similar_docs:
            logger.info(f"No relevant documents found for question: {question}")
            return {
                "retrieved_docs": [],
                "context": "",
                "sources": [],
                "has_documents": True,
                "needs_retrieval": False
            }
        
        # Format context and sources
        context = "\n\n".join([doc["content"] for doc in similar_docs])
        sources = list(set([doc["filename"] for doc in similar_docs]))
        
        logger.info(f"Retrieved {len(similar_docs)} documents for chat {chat_id}")
        
        return {
            "retrieved_docs": similar_docs,
            "context": context,
            "sources": sources,
            "has_documents": True,
            "needs_retrieval": True
        }
        
    except Exception as e:
        logger.error(f"Document retrieval failed for chat {chat_id}: {str(e)}")
        return {
            "retrieved_docs": [],
            "context": "",
            "sources": [],
            "has_documents": False,
            "needs_retrieval": False
        }
    