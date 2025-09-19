from fastapi import APIRouter
from services.embedding_service import generate_embedding
from services.vector_db_service import upsert_to_vector_db, tickets_index
from services.classification_service import classify_ticket
import json
from pathlib import Path

# Load tickets from the JSON file
tickets_file = Path(__file__).parent.parent / "data" / "sample_tickets.json"
with tickets_file.open() as f:
    tickets = json.load(f)

router = APIRouter()

@router.post("/classify")
async def classify_tickets():
    try:
        classified_count = 0
        for ticket in tickets:
            # Use 'body' field from the sample tickets, or 'content' if it exists
            content = ticket.get("body", ticket.get("content", ""))
            subject = ticket.get("subject", "")
            
            # Generate embedding
            embedding = await generate_embedding(content)
            
            # Classify the ticket
            classification = await classify_ticket(content, subject)
            
            # Flatten classification for Pinecone metadata (no nested objects allowed)
            ticket_with_classification = {
                **ticket,
                "topic": classification["topic"],
                "sentiment": classification["sentiment"],
                "priority": classification["priority"],
                "confidence": classification["confidence"],
                "topic_reasoning": classification["topic_reasoning"],
                "sentiment_reasoning": classification["sentiment_reasoning"],
                "priority_reasoning": classification["priority_reasoning"],
                "processing_time": 1.5,
                "cache_hit": False
            }
            
            # Store in vector database
            await upsert_to_vector_db("tickets", ticket["id"], embedding, ticket_with_classification)
            classified_count += 1
            
        return {
            "message": f"Successfully classified and stored {classified_count} tickets",
            "count": classified_count
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/")
async def get_tickets():
    """Retrieve all tickets from the vector database"""
    try:
        # Query all tickets from the vector database
        results = tickets_index.query(
            vector=[0] * 3072,  # Dummy vector for getting all results
            top_k=100,  # Get up to 100 tickets
            include_metadata=True
        )
        
        # Extract ticket data from results and reconstruct classification object
        ticket_list = []
        for match in results["matches"]:
            ticket_data = match["metadata"]
            ticket_data["id"] = match["id"]
            
            # Reconstruct classification object from flattened fields
            if "topic" in ticket_data:
                ticket_data["classification"] = {
                    "topic": ticket_data["topic"],
                    "sentiment": ticket_data["sentiment"],
                    "priority": ticket_data["priority"],
                    "confidence": ticket_data["confidence"],
                    "topic_reasoning": ticket_data["topic_reasoning"],
                    "sentiment_reasoning": ticket_data["sentiment_reasoning"],
                    "priority_reasoning": ticket_data["priority_reasoning"]
                }
            
            ticket_list.append(ticket_data)
        
        return {"tickets": ticket_list, "count": len(ticket_list)}
    except Exception as e:
        return {"error": str(e), "tickets": [], "count": 0}

@router.get("/sample")
async def get_sample_tickets():
    """Get sample tickets from the JSON file (for testing)"""
    try:
        return {"tickets": tickets, "count": len(tickets)}
    except Exception as e:
        return {"error": str(e), "tickets": [], "count": 0}
