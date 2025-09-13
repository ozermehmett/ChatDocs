import logging
from typing import Dict, Any
from agents.schemas.chat_state import ChatState
from models.ollama_chat import ollama_chat
from prompts.yaml_loader import prompt_loader

logger = logging.getLogger(__name__)

def generate_response(state: ChatState) -> Dict[str, Any]:
    """Generate chat response using LLM"""
    
    question = state["question"]
    context = state.get("context", "")
    sources = state.get("sources", [])
    chat_history = state.get("chat_history", [])
    has_documents = state.get("has_documents", False)
    
    try:
        # Get system prompt
        system_prompt = prompt_loader.get_system_prompt("chat_assistant")
        
        # Choose prompt template based on context availability
        if not has_documents or not context:
            # No documents available
            user_prompt = prompt_loader.format_prompt(
                "chat", "no_context",
                question=question
            )
        elif chat_history:
            # Has context and chat history
            chat_history_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in chat_history[-3:]  # Last 3 exchanges
            ])
            user_prompt = prompt_loader.format_prompt(
                "chat", "follow_up",
                chat_history=chat_history_text,
                context=context,
                sources=", ".join(sources),
                question=question
            )
        else:
            # Has context but no chat history
            user_prompt = prompt_loader.format_prompt(
                "chat", "rag_response",
                context=context,
                sources=", ".join(sources),
                question=question
            )
        
        # Format messages for model
        messages = ollama_chat.format_messages(
            system_prompt=system_prompt,
            user_message=user_prompt
        )
        
        # Generate response
        response = ollama_chat.generate_response(messages)
        
        logger.info(f"Generated response for question: {question[:50]}...")
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Response generation failed: {str(e)}")
        return {"response": f"Sorry, I encountered an error while generating a response: {str(e)}"}
    