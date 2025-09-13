from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from database import get_db, ChatSession, Message, Document
from services.document_service import document_service
from services.vector_service import vector_service
from models.ollama_chat import ollama_chat
from agents.workflows.chat_workflow import process_chat_message

router = APIRouter()

@router.post("/chat")
def create_chat(name: str, db: Session = Depends(get_db)):
    """Create new chat session"""
    chat = ChatSession(name=name)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    # Create vector collection for this chat
    vector_service.create_collection(chat.id)
    
    return {"id": chat.id, "name": chat.name, "created_at": chat.created_at}

@router.get("/chats")
def get_chats(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    chats = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    return [
        {
            "id": chat.id, 
            "name": chat.name, 
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        for chat in chats
    ]

@router.post("/chat/{chat_id}/upload")
async def upload_document(chat_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload document to chat"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Validate file type
    allowed_types = ['.pdf', '.txt', '.md']
    file_ext = '.' + file.filename.split('.')[-1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_types}")
    
    # Save file
    file_content = await file.read()
    file_path = document_service.save_file(file_content, file.filename, chat_id)
    
    # Process document
    doc_data = document_service.process_document(file_path)
    
    # Save to database
    document = Document(
        chat_session_id=chat_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_ext[1:]  # Remove the dot
    )
    db.add(document)
    db.commit()
    
    # Add to vector store
    vector_service.add_documents(chat_id, doc_data["chunks"], file.filename)
    
    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "chunks": doc_data["chunk_count"],
        "total_characters": len(doc_data["total_text"])
    }

@router.post("/chat/{chat_id}/message")
def send_message(chat_id: int, message: str, db: Session = Depends(get_db)):
    """Send message to chat using LangGraph workflow"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Check if Ollama is available
    if not ollama_chat.is_available():
        raise HTTPException(status_code=503, detail="Ollama service is not available")
    
    # Get chat history
    recent_messages = db.query(Message).filter(
        Message.chat_session_id == chat_id
    ).order_by(Message.timestamp.desc()).limit(6).all()
    
    # Format chat history (reverse to get chronological order)
    chat_history = []
    for msg in reversed(recent_messages):
        chat_history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Process message through workflow
    result = process_chat_message(chat_id, message, chat_history)
    
    # Save user message
    user_msg = Message(
        chat_session_id=chat_id,
        content=message,
        role="user"
    )
    db.add(user_msg)
    
    # Save assistant message
    assistant_msg = Message(
        chat_session_id=chat_id,
        content=result["response"],
        role="assistant",
        sources=json.dumps(result["sources"]) if result["sources"] else None
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "response": result["response"],
        "sources": result["sources"],
        "has_documents": result["has_documents"],
        "context_used": len(result["context"]) > 0
    }

@router.get("/chat/{chat_id}/messages")
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    """Get chat messages"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(
        Message.chat_session_id == chat_id
    ).order_by(Message.timestamp).all()
    
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "role": msg.role,
            "timestamp": msg.timestamp,
            "sources": json.loads(msg.sources) if msg.sources else []
        }
        for msg in messages
    ]

@router.delete("/chat/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """Delete chat session"""
    
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete vector collection
    vector_service.delete_collection(chat_id)
    
    # Delete from database (cascade will handle messages and documents)
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted successfully"}

@router.get("/chat/{chat_id}/documents")
def get_documents(chat_id: int, db: Session = Depends(get_db)):
    """Get documents for chat"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    documents = db.query(Document).filter(
        Document.chat_session_id == chat_id
    ).order_by(Document.processed_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "processed_at": doc.processed_at
        }
        for doc in documents
    ]
