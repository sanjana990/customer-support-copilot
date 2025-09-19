import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from typing import List, Dict, Set
import re
import hashlib
from pinecone import Pinecone, ServerlessSpec
import openai
from config.settings import PINECONE_API_KEY, OPENAI_API_KEY

class AtlanDocsRAGCrawler:
    def __init__(self):
        self.base_url = "https://docs.atlan.com"
        self.visited_urls: Set[str] = set()
        self.crawled_data: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = "atlan-docs-rag"
        self.index = None
        
        # Initialize OpenAI
        openai.api_key = OPENAI_API_KEY
    
    def setup_pinecone_index(self):
        """Create or connect to Pinecone index"""
        try:
            # Check if index exists
            if self.index_name in self.pc.list_indexes().names():
                print(f"✅ Connecting to existing index: {self.index_name}")
                self.index = self.pc.Index(self.index_name)
            else:
                print(f"🔄 Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=3072,  # text-embedding-3-large dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                time.sleep(1)  # Wait for index to be ready
                self.index = self.pc.Index(self.index_name)
            
            print(f"📊 Index stats: {self.index.describe_index_stats()}")
            return True
        except Exception as e:
            print(f"❌ Error setting up Pinecone: {e}")
            return False
    
    def crawl_and_store(self, max_pages: int = 100) -> bool:
        """Crawl Atlan documentation and store in Pinecone"""
        print(f"🚀 Starting comprehensive crawl of {self.base_url}")
        
        # Setup Pinecone
        if not self.setup_pinecone_index():
            return False
        
        # Start with main documentation pages
        seed_urls = [
            "https://docs.atlan.com",
            "https://docs.atlan.com/get-started",
            "https://docs.atlan.com/connect-data",
            "https://docs.atlan.com/use-data",
            "https://docs.atlan.com/build-governance",
            "https://docs.atlan.com/configure-atlan",
            "https://docs.atlan.com/build-with-atlan",
            "https://developer.atlan.com",
            "https://developer.atlan.com/sdks/",
            "https://developer.atlan.com/sdks/python/",
            "https://developer.atlan.com/sdks/java/",
            "https://developer.atlan.com/sdks/javascript/",
            "https://developer.atlan.com/sdks/go/",
            "https://docs.atlan.com/apps/connectors/business-intelligence/microsoft-power-bi/how-tos/set-up-microsoft-power-bi",
            "https://docs.atlan.com/apps/connectors/data-warehouses/snowflake/how-tos/set-up-snowflake",
            "https://docs.atlan.com/apps/connectors/data-warehouses/databricks/how-tos/set-up-databricks"
        ]
        
        queue = seed_urls.copy()
        stored_count = 0
        
        while queue and len(self.visited_urls) < max_pages:
            url = queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            try:
                print(f"📄 Crawling: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                self.visited_urls.add(url)
                
                # Extract and store page content
                success = self.extract_and_store_page(url, response.text)
                if success:
                    stored_count += 1
                
                # Find new URLs to crawl
                new_urls = self.extract_links(url, response.text)
                for new_url in new_urls:
                    if (new_url not in self.visited_urls and 
                        new_url not in queue and
                        self.is_atlan_docs_url(new_url)):
                        queue.append(new_url)
                
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"❌ Error crawling {url}: {e}")
                continue
        
        print(f"✅ Crawl completed. Stored {stored_count} pages in Pinecone")
        return True
    
    def extract_and_store_page(self, url: str, html: str) -> bool:
        """Extract content from page and store in Pinecone"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract title
            title = soup.find("title")
            title_text = title.get_text().strip() if title else ""
            
            # Extract main content
            main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content"))
            content_text = main_content.get_text().strip() if main_content else ""
            
            # Clean and chunk content
            if len(content_text) < 100:  # Skip pages with too little content
                return False
            
            # Create chunks
            chunks = self.create_chunks(content_text, title_text, url)
            
            # Store each chunk in Pinecone
            for i, chunk in enumerate(chunks):
                self.store_chunk_in_pinecone(chunk, url, i)
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting content from {url}: {e}")
            return False
    
    def create_chunks(self, content: str, title: str, url: str) -> List[Dict]:
        """Create chunks from content for better retrieval"""
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        chunks = []
        current_chunk = title + "\n\n" if title else ""
        chunk_size = 0
        max_chunk_size = 1000  # characters
        
        for sentence in sentences:
            if chunk_size + len(sentence) > max_chunk_size and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "url": url,
                    "title": title
                })
                current_chunk = sentence + ". "
                chunk_size = len(sentence)
            else:
                current_chunk += sentence + ". "
                chunk_size += len(sentence)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "url": url,
                "title": title
            })
        
        return chunks
    
    def store_chunk_in_pinecone(self, chunk: Dict, url: str, chunk_index: int):
        """Store a chunk in Pinecone with embedding"""
        try:
            # Generate embedding
            embedding = self.generate_embedding(chunk["content"])
            
            if not embedding:
                return
            
            # Create unique ID
            chunk_id = hashlib.md5(f"{url}_{chunk_index}".encode()).hexdigest()
            
            # Store in Pinecone
            self.index.upsert(vectors=[{
                "id": chunk_id,
                "values": embedding,
                "metadata": {
                    "content": chunk["content"],
                    "url": url,
                    "title": chunk.get("title", ""),
                    "chunk_index": chunk_index
                }
            }])
            
        except Exception as e:
            print(f"❌ Error storing chunk in Pinecone: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-3-large"
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return []
    
    def extract_links(self, base_url: str, html: str) -> List[str]:
        """Extract all links from a page"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            links.append(full_url)
        
        return links
    
    def is_atlan_docs_url(self, url: str) -> bool:
        """Check if URL is from Atlan documentation"""
        parsed = urlparse(url)
        return (parsed.netloc in ["docs.atlan.com", "developer.atlan.com"] and
                not any(skip in url.lower() for skip in [".pdf", ".zip", ".exe", "#", "mailto:", "tel:"]))
    
    def search_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant content in Pinecone"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.matches
            
        except Exception as e:
            print(f"❌ Error searching Pinecone: {e}")
            return []

# Global instance
rag_crawler = AtlanDocsRAGCrawler()
