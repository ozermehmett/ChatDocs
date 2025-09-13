from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="chat_session", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="chat_session", cascade="all, delete-orphan")

class Message(Base):
    """Message model for chat history"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    sources = Column(Text, nullable=True)  # JSON string of source documents
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")

class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, txt, md
    processed_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="documents")

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        