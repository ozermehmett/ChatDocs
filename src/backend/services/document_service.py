import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
from config import settings

logger = logging.getLogger(__name__)

class DocumentService:
    """Document processing service for PDF, TXT, MD files"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
    
    def save_file(self, file_content: bytes, filename: str, chat_id: int) -> str:
        """Save uploaded file to chat directory"""
        chat_dir = self.upload_dir / f"chat_{chat_id}"
        chat_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = chat_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        return str(file_path)
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from document based on file type"""
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext == ".pdf":
                return self._extract_pdf_text(file_path)
            elif file_ext == ".txt":
                return self._extract_txt_text(file_path)
            elif file_ext == ".md":
                return self._extract_md_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    
    def _extract_md_text(self, file_path: Path) -> str:
        """Extract text from MD file"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find last sentence boundary within chunk
            if end < len(text):
                last_sentence = text.rfind(".", start, end)
                if last_sentence > start:
                    end = last_sentence + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document and return chunks with metadata"""
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return {
            "file_path": file_path,
            "filename": Path(file_path).name,
            "total_text": text,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }

# Global instance
document_service = DocumentService()
