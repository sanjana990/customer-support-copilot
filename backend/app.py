from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.tickets_controller import router as tickets_router
from controllers.rag_controller import router as rag_router

app = FastAPI(title="Atlan Customer Support Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tickets_router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])

@app.get("/")
def root():
    return {"message": "Atlan Customer Support Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/init")
async def initialize_data():
    """Initialize the system by classifying sample tickets"""
    from controllers.tickets_controller import classify_tickets
    return await classify_tickets()