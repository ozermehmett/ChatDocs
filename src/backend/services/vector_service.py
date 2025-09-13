import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from services.embedding_service import embedding_service
from config import settings

logger = logging.getLogger(__name__)

class VectorService:
    """ChromaDB vector store operations"""
    
    def __init__(self):
        self.chroma_path = Path(settings.CHROMA_DB_PATH)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    
    def get_collection_name(self, chat_id: int) -> str:
        """Get collection name for chat session"""
        return f"chat_{chat_id}"
    
    def create_collection(self, chat_id: int) -> None:
        """Create collection for chat session"""
        collection_name = self.get_collection_name(chat_id)
        
        try:
            self.client.create_collection(
                name=collection_name,
                metadata={"chat_id": chat_id}
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            if "already exists" not in str(e):
                logger.error(f"Failed to create collection {collection_name}: {str(e)}")
                raise
    
    def get_collection(self, chat_id: int):
        """Get collection for chat session"""
        collection_name = self.get_collection_name(chat_id)
        return self.client.get_collection(name=collection_name)
    
    def add_documents(self, chat_id: int, chunks: List[str], filename: str) -> None:
        """Add document chunks to vector store"""
        try:
            collection = self.get_collection(chat_id)
            
            # Get embeddings for chunks
            embeddings = embedding_service.get_embeddings(chunks)
            
            # Generate IDs and metadata
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_text": chunk[:100]  # First 100 chars for preview
                }
                for i, chunk in enumerate(chunks)
            ]
            
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks from {filename} to collection")
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {str(e)}")
            raise Exception(f"Vector store operation failed: {str(e)}")
    
    def search_similar(self, chat_id: int, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            collection = self.get_collection(chat_id)
            
            # Get query embedding
            query_embedding = embedding_service.get_single_embedding(query)
            
            # Search similar documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "filename": results["metadatas"][0][i]["filename"],
                        "chunk_index": results["metadatas"][0][i]["chunk_index"],
                        "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vector store: {str(e)}")
            return []
    
    def delete_collection(self, chat_id: int) -> None:
        """Delete collection for chat session"""
        try:
            collection_name = self.get_collection_name(chat_id)
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
    
    def collection_exists(self, chat_id: int) -> bool:
        """Check if collection exists for chat session"""
        try:
            collection_name = self.get_collection_name(chat_id)
            collections = self.client.list_collections()
            return any(col.name == collection_name for col in collections)
        except:
            return False

# Global instance
vector_service = VectorService()
