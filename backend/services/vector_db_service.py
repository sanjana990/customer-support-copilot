import pinecone
from config.settings import PINECONE_API_KEY, PINECONE_TICKETS_INDEX, PINECONE_DOCS_INDEX
from services.embedding_service import generate_embedding

# Initialize Pinecone client
pinecone.init(api_key=PINECONE_API_KEY)

# Initialize indexes
tickets_index = pinecone.Index(PINECONE_TICKETS_INDEX)
docs_index = pinecone.Index(PINECONE_DOCS_INDEX)

async def upsert_to_vector_db(index_name: str, id: str, embedding: list, metadata: dict):
    index = tickets_index if index_name == "tickets" else docs_index
    index.upsert([(id, embedding, metadata)])

async def retrieve_from_vector_db(index_name: str, query: str, top_k: int = 5):
    index = tickets_index if index_name == "tickets" else docs_index
    embedding = await generate_embedding(query)
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    
    # Build context with source information
    context_parts = []
    for match in results["matches"]:
        content = match["metadata"].get("content", "")
        source = match["metadata"].get("source", "")
        url = match["metadata"].get("url", "")
        
        if source and url:
            context_parts.append(f"Source: {source}\nURL: {url}\nContent: {content}\n")
        else:
            context_parts.append(content)
    
    return "\n".join(context_parts)

async def retrieve_with_sources(index_name: str, query: str, top_k: int = 5):
    """Retrieve context and return both content and source information"""
    index = tickets_index if index_name == "tickets" else docs_index
    embedding = await generate_embedding(query)
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    
    sources = []
    context_parts = []
    
    for match in results["matches"]:
        content = match["metadata"].get("content", "")
        source = match["metadata"].get("source", "")
        url = match["metadata"].get("url", "")
        
        if source and url:
            sources.append({"doc": source, "url": url})
            context_parts.append(f"Source: {source}\nURL: {url}\nContent: {content}\n")
        else:
            context_parts.append(content)
    
    return "\n".join(context_parts), sources
