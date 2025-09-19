# Atlan AI Assistant - Backend

FastAPI backend for the Atlan AI Assistant with RAG capabilities and intelligent ticket classification.

## 🚀 Quick Deploy to Render

### 1. Environment Variables
Set these in your Render dashboard:
```
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=atlan-docs-rag
```

### 2. Build & Start Commands
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. Health Check
The app exposes a health check endpoint at `/health` for Render's health monitoring.

## 📊 API Endpoints

- `GET /health` - Health check
- `POST /api/rag/query` - RAG query endpoint
- `GET /api/tickets/` - Get all tickets
- `POST /api/tickets/` - Create new ticket

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="your-env"

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Key Files

- `app.py` - FastAPI application entry point
- `controllers/rag_controller.py` - RAG query handling
- `services/atlan_rag_service.py` - RAG implementation
- `services/classification_service.py` - AI classification
- `requirements.txt` - Python dependencies
