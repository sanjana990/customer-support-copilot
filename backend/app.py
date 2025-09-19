import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.tickets_controller import router as tickets_router
from controllers.rag_controller import router as rag_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Atlan Customer Support Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tickets_router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Atlan Customer Support Backend starting up...")
    logger.info("✅ CORS middleware configured")
    logger.info("✅ Routes included")
    logger.info("🎉 Application ready!")

@app.get("/")
def root():
    logger.info("📡 Root endpoint accessed")
    return {"message": "Atlan Customer Support Backend is running!"}

@app.get("/health")
def health_check():
    logger.info("🏥 Health check endpoint accessed")
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/init")
async def initialize_data():
    """Initialize the system by classifying sample tickets"""
    logger.info("🔧 Initializing data...")
    from controllers.tickets_controller import classify_tickets
    return await classify_tickets()
# Force deployment update
