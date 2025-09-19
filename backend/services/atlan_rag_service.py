import openai
from typing import List, Dict
from services.atlan_rag_crawler import atlan_rag_crawler
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class AtlanRAGService:
    def __init__(self):
        self.crawler = atlan_rag_crawler
    
    async def generate_rag_response(self, query: str, top_k: int = 5) -> Dict:
        """Generate RAG response using crawled content from Pinecone"""
        try:
            # Step 1: Ensure crawler is connected to Pinecone
            if not self.crawler.index:
                print("🔄 Connecting crawler to Pinecone...")
                self.crawler.setup_pinecone_index()
            
            # Step 2: Search for relevant content in Pinecone
            print(f"🔍 Searching Pinecone for: {query}")
            search_results = self.crawler.search_content(query, top_k)
            
            if not search_results:
                return {
                    "answer": "I couldn't find relevant information in the Atlan documentation for your query. Please try rephrasing your question or contact support for assistance.",
                    "citations": [],
                    "sources": []
                }
            
            # Step 2: Extract content and sources (deduplicate URLs)
            context_parts = []
            citations = []
            sources = []
            seen_urls = set()  # Track unique URLs
            
            print(f"�� Processing {len(search_results)} search results for deduplication...")
            
            for i, result in enumerate(search_results):
                content = result.metadata.get("content", "")
                url = result.metadata.get("url", "")
                title = result.metadata.get("title", "")
                score = result.score
                
                print(f"   Result {i+1}: URL='{url}', Title='{title[:50]}...', Score={score:.3f}")
                
                if content and url:
                    # Always add content for context (even if URL is duplicate)
                    context_parts.append(content)
                    
                    # Only add citation if URL is unique
                    if url not in seen_urls:
                        citations.append({
                            "doc": title or "Atlan Documentation",
                            "url": url
                        })
                        seen_urls.add(url)
                        print(f"     ✅ Added unique citation: {url}")
                    else:
                        print(f"     ⚠️  Skipped duplicate URL: {url}")
                    
                    # Always add to sources for debugging
                    sources.append({
                        "content": content,
                        "url": url,
                        "title": title,
                        "relevance_score": score
                    })
            
            print(f"📊 Final deduplication results: {len(citations)} unique citations from {len(search_results)} results")
            
            # Step 3: Combine context
            context = "\n\n".join(context_parts)
            
            # Step 4: Generate response using only the retrieved content
            answer = await self.generate_response_from_context(query, context)
            
            return {
                "answer": answer,
                "citations": citations,
                "sources": sources,
                "context_used": len(context_parts)
            }
            
        except Exception as e:
            print(f"❌ Error in RAG service: {e}")
            return {
                "answer": "I encountered an error while processing your request. Please try again or contact support.",
                "citations": [],
                "sources": []
            }
    
    async def generate_response_from_context(self, query: str, context: str) -> str:
        """Generate response using only the provided context"""
        prompt = f"""You are an expert Atlan customer support assistant. Based ONLY on the following context from Atlan documentation, provide a comprehensive answer to the user's question.

IMPORTANT: 
- Use ONLY the information provided in the context below
- Do not use any external knowledge or training data
- If the context doesn't contain enough information, say so clearly
- Be specific and actionable in your response
- Include relevant code examples if available in the context

User Query: {query}

Context from Atlan Documentation:
{context}

Please provide a helpful and accurate response based on the context above."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again or contact support for assistance."

# Global instance
atlan_rag_service = AtlanRAGService()
