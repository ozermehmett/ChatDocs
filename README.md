# ChatDocs

A document-based chat application that allows you to have conversations with your documents using local AI models.

## Demo

![Demo Video](./assets/demo.mp4)

## Features

- Upload PDF, TXT, and MD documents
- Chat with documents using AI
- Multiple chat sessions
- Local processing with Ollama
- Vector-based document search

## Quick Start

### Prerequisites

- Docker and Docker Compose
- [Ollama](https://ollama.ai/) installed and running locally
- Ollama model downloaded (e.g., `ollama pull mistral`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ozermehmett/ChatDocs.git
cd ChatDocs
```

2. Start the application:
```bash
docker-compose up --build
```

3. Open your browser and go to:
   - **Frontend:** http://localhost:8501
   - **Backend API:** http://localhost:8080/docs

## Usage

1. **Create a Chat:** Click "New Chat" in the left sidebar
2. **Upload Documents:** Drag and drop files in the right panel
3. **Ask Questions:** Type your questions in the chat input
4. **View Sources:** Click on source citations to see referenced documents

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (served by Nginx)
- **Backend:** FastAPI, SQLAlchemy, ChromaDB
- **AI:** Ollama (local LLM), LangGraph workflows
- **Database:** SQLite
- **Containerization:** Docker, Docker Compose

## Architecture

- **Frontend:** 3-panel interface
- **Backend:** RESTful API with document processing
- **Vector Store:** ChromaDB for semantic search
- **Embedding Service:** Custom embedding API
- **AI Processing:** LangGraph workflows with Ollama

## Configuration

Environment variables can be configured in `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://localhost:11434
  - OLLAMA_MODEL=mistral
  - DEBUG=False
```

## License

MIT License - see the [LICENSE](LICENSE) file for details