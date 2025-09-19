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

class ImprovedAtlanRAGCrawler:
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
                print(f"📊 Connecting to existing Pinecone index: {self.index_name}")
                self.index = self.pc.Index(self.index_name)
            else:
                print(f"🆕 Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=3072,  # OpenAI ada-002 embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                self.index = self.pc.Index(self.index_name)
            
            return True
        except Exception as e:
            print(f"❌ Error setting up Pinecone: {e}")
            return False
    
    def crawl_and_store(self, max_pages: int = 100) -> bool:
        """Crawl documentation and store in Pinecone with improved content extraction"""
        print(f"🚀 Starting improved crawl of {self.base_url}")
        
        # Setup Pinecone
        if not self.setup_pinecone_index():
            return False
        
        # Start with main documentation pages, prioritizing SDK pages
        seed_urls = [
            "https://developer.atlan.com/sdks/python/",  # Priority: Python SDK
            "https://developer.atlan.com/sdks/java/",
            "https://developer.atlan.com/sdks/go/",
            "https://developer.atlan.com/sdks/kotlin/",
            "https://developer.atlan.com/sdks/scala/",
            "https://docs.atlan.com",
            "https://docs.atlan.com/get-started",
            "https://docs.atlan.com/connect-data",
            "https://docs.atlan.com/use-data",
            "https://docs.atlan.com/build-governance",
            "https://docs.atlan.com/configure-atlan",
            "https://docs.atlan.com/build-with-atlan",
            "https://developer.atlan.com"
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
                
                # Extract and store page content with improved extraction
                success = self.extract_and_store_page_improved(url, response.text)
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
        
        print(f"✅ Improved crawl completed. Stored {stored_count} pages in Pinecone")
        return True
    
    def extract_and_store_page_improved(self, url: str, html: str) -> bool:
        """Extract content from page and store in Pinecone with improved content extraction"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract title
            title = soup.find("title")
            title_text = title.get_text().strip() if title else ""
            
            # IMPROVED: Extract all relevant content, not just main
            content_parts = []
            
            # Try multiple selectors for content
            content_selectors = [
                "main",
                "article", 
                "div.content",
                "div.documentation",
                "div.page-content",
                "div.markdown-body",
                "div.rst-content",
                "div.sphinx-content",
                "[role='main']",
                ".content",
                ".documentation",
                ".page-content"
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                # Extract all text content
                content_text = main_content.get_text(separator='\n', strip=True)
                
                # Also extract code blocks separately for better preservation
                code_blocks = main_content.find_all(['pre', 'code'])
                for code_block in code_blocks:
                    if code_block.name == 'pre':
                        # This is a code block
                        code_text = code_block.get_text()
                        content_text += f"\n\nCode Example:\n{code_text}\n"
                    elif code_block.name == 'code' and code_block.parent.name == 'pre':
                        # This is inside a pre block, already handled
                        continue
                    else:
                        # Inline code
                        code_text = code_block.get_text()
                        content_text += f" `{code_text}` "
            else:
                # Fallback: extract from body
                body = soup.find("body")
                content_text = body.get_text(separator='\n', strip=True) if body else ""
            
            # Clean up content
            content_text = self.clean_content(content_text)
            
            # Skip pages with too little content
            if len(content_text) < 100:
                return False
            
            # Create chunks with larger size for better context
            chunks = self.create_improved_chunks(content_text, title_text, url)
            
            # Store each chunk in Pinecone
            for i, chunk in enumerate(chunks):
                self.store_chunk_in_pinecone(chunk, url, i)
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting content from {url}: {e}")
            return False
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        # Remove leading/trailing whitespace
        content = content.strip()
        # Normalize spaces
        content = re.sub(r' +', ' ', content)
        return content
    
    def create_improved_chunks(self, content: str, title: str, url: str) -> List[Dict]:
        """Create chunks from content for better retrieval with larger chunk size"""
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        chunks = []
        current_chunk = title + "\n\n" if title else ""
        chunk_size = 0
        max_chunk_size = 2000  # INCREASED: 2000 characters for better context
        
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
        """Store a chunk in Pinecone"""
        try:
            # Generate embedding
            embedding = self.generate_embedding(chunk["content"])
            
            # Create unique ID
            chunk_id = f"{hashlib.md5(url.encode()).hexdigest()}_{chunk_index}"
            
            # Prepare metadata
            metadata = {
                "url": url,
                "title": chunk["title"],
                "content": chunk["content"],
                "chunk_index": chunk_index
            }
            
            # Store in Pinecone
            self.index.upsert(vectors=[{
                "id": chunk_id,
                "values": embedding,
                "metadata": metadata
            }])
            
        except Exception as e:
            print(f"❌ Error storing chunk in Pinecone: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return []
    
    def search_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for content in Pinecone"""
        try:
            if not self.index:
                print("❌ Pinecone index not initialized")
                return []
            
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
            
            return results["matches"]
            
        except Exception as e:
            print(f"❌ Error searching content: {e}")
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
