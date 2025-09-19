import pinecone
import openai
import requests
from bs4 import BeautifulSoup
from config.settings import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_DOCS_INDEX
import time
import json
import re

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

class ImprovedAtlanRAGCrawler:
    def __init__(self):
        self.index = None
        self.setup_pinecone_index()
    
    def setup_pinecone_index(self):
        """Setup Pinecone index for storing crawled content"""
        try:
            # Check if index exists
            if PINECONE_DOCS_INDEX not in pinecone.list_indexes():
                # Create index if it doesn't exist
                pinecone.create_index(
                    name=PINECONE_DOCS_INDEX,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
                print(f"Created Pinecone index: {PINECONE_DOCS_INDEX}")
            
            # Connect to index
            self.index = pinecone.Index(PINECONE_DOCS_INDEX)
            print(f"Connected to Pinecone index: {PINECONE_DOCS_INDEX}")
            
        except Exception as e:
            print(f"Error setting up Pinecone index: {e}")
            self.index = None
    
    def generate_embedding(self, text: str) -> list:
        """Generate embedding for text using OpenAI"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def create_chunks(self, content: str, max_chunk_size: int = 2000) -> list:
        """Split content into chunks for better retrieval"""
        if not content:
            return []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, save current chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def crawl_atlan_docs(self, base_url: str = "https://developer.atlan.com"):
        """Crawl Atlan documentation and store in Pinecone"""
        if not self.index:
            print("Pinecone index not available")
            return
        
        # URLs to crawl
        urls_to_crawl = [
            f"{base_url}/sdks/python/",
            f"{base_url}/sdks/java/",
            f"{base_url}/sdks/kotlin/",
            f"{base_url}/sdks/scala/",
            f"{base_url}/sdks/go/",
            f"{base_url}/sdks/javascript/",
            f"{base_url}/connectors/snowflake/",
            f"{base_url}/connectors/databricks/",
            f"{base_url}/connectors/powerbi/",
            f"{base_url}/connectors/tableau/",
            f"{base_url}/sso/saml/",
            f"{base_url}/sso/oidc/",
        ]
        
        for url in urls_to_crawl:
            try:
                print(f"Crawling: {url}")
                self.crawl_and_store_page(url)
                time.sleep(1)  # Be respectful to the server
            except Exception as e:
                print(f"Error crawling {url}: {e}")
    
    def crawl_and_store_page(self, url: str):
        """Crawl a single page and store its content in Pinecone"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '.documentation', '.docs-content', 'div[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator='\n', strip=True)
                    break
            
            if not content:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            if content:
                # Create chunks
                chunks = self.create_chunks(content)
                
                # Store each chunk in Pinecone
                for i, chunk in enumerate(chunks):
                    if chunk.strip():
                        # Generate embedding
                        embedding = self.generate_embedding(chunk)
                        
                        if embedding:
                            # Create unique ID
                            chunk_id = f"{url.replace('/', '_').replace(':', '_')}_{i}"
                            
                            # Store in Pinecone
                            self.index.upsert([(
                                chunk_id,
                                embedding,
                                {
                                    "content": chunk,
                                    "url": url,
                                    "title": title_text,
                                    "chunk_index": i
                                }
                            )])
                            
                            print(f"Stored chunk {i} from {url}")
                
        except Exception as e:
            print(f"Error crawling page {url}: {e}")
    
    def search_content(self, query: str, top_k: int = 5) -> list:
        """Search for relevant content in Pinecone"""
        if not self.index:
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results['matches']
            
        except Exception as e:
            print(f"Error searching content: {e}")
            return []

# Initialize crawler
improved_atlan_rag_crawler = ImprovedAtlanRAGCrawler()
