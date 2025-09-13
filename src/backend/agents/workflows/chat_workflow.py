import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from agents.schemas.chat_state import ChatState
from agents.nodes.retrieve_node import retrieve_documents
from agents.nodes.chat_node import generate_response
from agents.nodes.memory_node import load_chat_history, save_chat_message

logger = logging.getLogger(__name__)

def create_chat_workflow():
    """Create LangGraph workflow for chat processing"""
    
    # Create workflow graph
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("load_memory", load_chat_history)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("generate", generate_response)
    workflow.add_node("save_message", save_chat_message)
    
    # Define workflow edges
    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "save_message")
    workflow.add_edge("save_message", END)
    
    # Compile workflow
    app = workflow.compile()
    
    logger.info("Chat workflow created successfully")
    return app

def process_chat_message(chat_id: int, question: str, chat_history: list = None) -> Dict[str, Any]:
    """Process chat message through workflow"""
    
    try:
        # Create workflow
        workflow = create_chat_workflow()
        
        # Initial state
        initial_state = {
            "chat_id": chat_id,
            "question": question,
            "chat_history": chat_history or [],
            "retrieved_docs": None,
            "context": None,
            "sources": None,
            "response": None,
            "has_documents": False,
            "needs_retrieval": False
        }
        
        # Run workflow
        result = workflow.invoke(initial_state)
        
        logger.info(f"Chat workflow completed for chat {chat_id}")
        
        return {
            "response": result.get("response", ""),
            "sources": result.get("sources", []),
            "context": result.get("context", ""),
            "has_documents": result.get("has_documents", False)
        }
        
    except Exception as e:
        logger.error(f"Chat workflow failed for chat {chat_id}: {str(e)}")
        return {
            "response": f"Sorry, I encountered an error while processing your message: {str(e)}",
            "sources": [],
            "context": "",
            "has_documents": False
        }
    