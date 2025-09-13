from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from database import get_db, ChatSession, Message, Document
from services.document_service import document_service
from services.vector_service import vector_service

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
        {"id": chat.id, "name": chat.name, "created_at": chat.created_at}
        for chat in chats
    ]

@router.post("/chat/{chat_id}/upload")
async def upload_document(chat_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload document to chat"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
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
        file_type=file.filename.split('.')[-1].lower()
    )
    db.add(document)
    db.commit()
    
    # Add to vector store
    vector_service.add_documents(chat_id, doc_data["chunks"], file.filename)
    
    return {"message": "Document uploaded successfully", "chunks": doc_data["chunk_count"]}

@router.post("/chat/{chat_id}/message")
def send_message(chat_id: int, message: str, db: Session = Depends(get_db)):
    """Send message to chat"""
    
    # Check if chat exists
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_msg = Message(
        chat_session_id=chat_id,
        content=message,
        role="user"
    )
    db.add(user_msg)
    db.commit()
    
    # Search similar documents
    similar_docs = vector_service.search_similar(chat_id, message, n_results=3)
    
    # Create context from similar documents
    context = "\n\n".join([doc["content"] for doc in similar_docs])
    sources = [doc["filename"] for doc in similar_docs]
    
    # Simple response for now (will be replaced with LLM later)
    response = f"Based on your documents, I found relevant information. Context length: {len(context)} characters. Sources: {', '.join(set(sources))}"
    
    # Save assistant message
    assistant_msg = Message(
        chat_session_id=chat_id,
        content=response,
        role="assistant",
        sources=str(sources)
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "response": response,
        "sources": sources,
        "context_length": len(context)
    }

@router.get("/chat/{chat_id}/messages")
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    """Get chat messages"""
    messages = db.query(Message).filter(Message.chat_session_id == chat_id).order_by(Message.timestamp).all()
    
    return [
        {
            "content": msg.content,
            "role": msg.role,
            "timestamp": msg.timestamp,
            "sources": msg.sources
        }
        for msg in messages
    ]
