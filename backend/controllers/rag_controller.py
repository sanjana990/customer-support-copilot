from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_db_service import retrieve_from_vector_db, retrieve_with_sources
from services.embedding_service import generate_response
from services.classification_service import classify_ticket
from services.atlan_rag_service import atlan_rag_service
from services.crawled_data_url_resolver import url_resolver
import time

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    channel: str = "Web Chat"
    session_id: str = "default"
    include_followup: bool = True

class QueryResponse(BaseModel):
    answer: str
    citations: list = []
    classification: dict
    classification_reasons: dict
    processing_time: float
    cache_hit: bool = False
    followup_suggestions: list = []
    session_id: str
    response_type: str  # "rag_response" or "routing_message"

def is_atlan_related_query(query: str, classification: dict) -> bool:
    """
    Intelligently determine if a query is related to Atlan using AI classification
    and semantic understanding rather than keyword matching.
    """
    query_lower = query.lower()
    
    # Get classification reasoning to understand the AI's analysis
    topic_reasoning = classification.get("topic_reasoning", "").lower()
    topic = classification.get("topic", "").lower()
    
    # Check if the AI classifier explicitly identified Atlan-related context
    atlan_indicators = [
        "atlan", "data catalog", "data lineage", "data governance", "metadata",
        "api", "sdk", "integration", "connector", "sso", "authentication",
        "snowflake", "databricks", "powerbi", "tableau", "looker", "dbt",
        "airflow", "kafka", "mongodb", "postgres", "mysql", "bigquery",
        "redshift", "athena", "s3", "azure", "gcp", "google cloud"
    ]
    
    # If the query explicitly mentions Atlan or data-related terms, it's related
    if any(indicator in query_lower for indicator in atlan_indicators):
        return True
    
    # Check if the AI's reasoning suggests Atlan-related context
    if any(indicator in topic_reasoning for indicator in atlan_indicators):
        return True
    
    # Check if the topic classification suggests technical/data context
    technical_topics = ["api/sdk", "integration", "sso", "how-to", "product", "best practices", "connector", "lineage", "glossary", "sensitive data"]
    if topic in technical_topics:
        return True
    
    # If the AI classified it as "General" but the reasoning doesn't mention
    # any Atlan-specific context, it's likely unrelated
    if topic == "general":
        # Check if the reasoning explicitly mentions non-Atlan topics
        non_atlan_indicators = [
            "cooking", "recipe", "food", "curry", "pasta", "weather", "sports",
            "movie", "music", "game", "travel", "shopping", "personal", "health",
            "finance", "news", "politics", "religion", "dating", "family"
        ]
        
        if any(indicator in topic_reasoning for indicator in non_atlan_indicators):
            return False
        
        # If it's general and doesn't contain Atlan keywords, it's unrelated
        if not any(indicator in query_lower for indicator in atlan_indicators):
            return False
    
    # Default to related if we can't determine otherwise
    return True

def generate_contextual_followup_questions(topic: str, query: str, answer: str) -> list:
    """Generate contextual follow-up questions using AI based on the user's query and answer"""
    try:
        import openai
        from config.settings import OPENAI_API_KEY
        
        # Set the API key for older versions
        openai.api_key = OPENAI_API_KEY
        
        # Create a prompt for AI to generate contextual follow-up questions
        followup_prompt = f"""
        Based on this user query and the provided answer, generate 3 relevant follow-up questions that a user might naturally ask next.
        
        User Query: "{query}"
        Topic: {topic}
        Answer: "{answer[:200]}..." (truncated for context)
        
        The follow-up questions should:
        1. Be specific to the user's query and context
        2. Show natural progression from their original question
        3. Be actionable and helpful
        4. Cover different aspects of the topic they're asking about
        5. Be phrased as natural follow-up questions
        
        Examples of good follow-up questions:
        - For webhook queries: "How do I test if my webhook is working correctly?"
        - For SDK queries: "What are the common error codes I should handle?"
        - For authentication queries: "How do I rotate my API keys securely?"
        - For setup queries: "What are the system requirements for this?"
        
        Respond with exactly 3 follow-up questions, one per line, without numbering or bullets.
        Each question should be a complete, natural question that flows from the original query.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": followup_prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        # Parse AI response - fix the string splitting
        ai_questions = response.choices[0].message.content.strip().split('\n')
        ai_questions = [q.strip() for q in ai_questions if q.strip()]
        
        # Format as required by the API
        followup_suggestions = [{"question": q} for q in ai_questions[:3]]
        
        print(f"DEBUG: AI-generated follow-up questions: {followup_suggestions}")
        return followup_suggestions
        
    except Exception as e:
        print(f"DEBUG: AI follow-up generation failed: {e}, using fallback")
        # Fallback to topic-based questions
        if topic == "API/SDK":
            return [
                {"question": "Can you show me a code example for this?"},
                {"question": "What are the common error codes I should handle?"},
                {"question": "How do I handle authentication properly?"}
            ]
        elif topic == "SSO":
            return [
                {"question": "How do I configure this step by step?"},
                {"question": "What identity providers are supported?"},
                {"question": "How do I troubleshoot if it doesn't work?"}
            ]
        elif topic == "How-to":
            return [
                {"question": "Can you provide more detailed steps?"},
                {"question": "What are the prerequisites I need?"},
                {"question": "What if I encounter errors during setup?"}
            ]
        else:
            return [
                {"question": "Can you provide more details about this?"},
                {"question": "What are the next steps I should take?"},
                {"question": "How can I get additional help?"}
            ]

# Define RAG topics
rag_topics = ['How-to', 'Product', 'Best practices', 'API/SDK', 'SSO']
@router.post("/query")
async def query_rag(request: QueryRequest):
    """Handle RAG queries with intelligent URL selection"""
    start_time = time.time()
    
    try:
        # Step 1: Classify the query (pass empty subject for consistency with tickets controller)
        classification = await classify_ticket(request.query, '')
        print(f"DEBUG: Classification result: {classification}")
        
        # Step 2: Check if query is Atlan-related
        if not is_atlan_related_query(request.query, classification):
            print("DEBUG: Query not Atlan-related, providing rejection message")
            return QueryResponse(
                answer="I'm sorry, but I can only help with Atlan-related questions. Please ask me about Atlan's features, setup, troubleshooting, or any other Atlan-specific topics.",
                citations=[],
                followup_suggestions=[
                    {"question": "What Atlan features can you help me with?"},
                    {"question": "How do I get started with Atlan?"},
                    {"question": "What are Atlan's main capabilities?"}
                ],
                response_type="rag_response",
                processing_time=0,
                session_id=request.session_id
            )
        
        # Step 3: Determine if we should use RAG
        use_rag = classification["topic"] in rag_topics
        print(f"DEBUG: Use RAG: {use_rag}")
        
        if use_rag:
            # Step 4: Use proper RAG with crawled content from Pinecone
            print("DEBUG: Using proper RAG with crawled content from Pinecone")
            rag_result = await atlan_rag_service.generate_rag_response(request.query, top_k=5)
            
            answer = rag_result["answer"]
            citations = rag_result["citations"]
            sources = rag_result.get("sources", [])
            context_used = rag_result.get("context_used", 0)
            
            print(f"DEBUG: RAG result - Context chunks used: {context_used}, Citations: {len(citations)}")
            response_type = "rag_response"
        else:
            # Step 5: Generate routing message for other topics (Connector, Lineage, Glossary, Sensitive data, General)
            answer = f"Thank you for your {classification['topic'].lower()} inquiry. I'll route this to the appropriate team for assistance. Our specialists will review your request and provide detailed guidance."
            response_type = "routing_message"
            citations = []
        
        # Step 6: Generate follow-up suggestions ONLY for RAG responses
        followup_suggestions = []
        if use_rag:
            # Only generate follow-ups for RAG responses (direct answers)
            followup_suggestions = generate_contextual_followup_questions(
                classification["topic"], 
                request.query, 
                answer
            )
        # For routed queries (non-RAG), no follow-ups - the routed team will handle them
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            classification=classification,
            classification_reasons={
                "topic_reasoning": classification.get("topic_reasoning", ""),
                "sentiment_reasoning": classification.get("sentiment_reasoning", ""),
                "priority_reasoning": classification.get("priority_reasoning", "")
            },
            followup_suggestions=followup_suggestions,
            response_type=response_type,
            processing_time=processing_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        print(f"Error in query_rag: {e}")
        return QueryResponse(
            answer="I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.",
            citations=[],
            classification={"topic": "General", "sentiment": "Neutral", "priority": "P3", "confidence": 0.0},
            classification_reasons={
                "topic_reasoning": "Error occurred during processing",
                "sentiment_reasoning": "Unable to determine sentiment due to error",
                "priority_reasoning": "Error requires immediate attention"
            },
            followup_suggestions=[
                {"question": "How can I contact support?"},
                {"question": "What should I do if this error continues?"},
                {"question": "Is there an alternative way to get help?"}
            ],
            response_type="rag_response",
            processing_time=0,
            session_id=request.session_id
        )
