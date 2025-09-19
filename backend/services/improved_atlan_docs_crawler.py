import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from typing import List, Dict, Set
import re

class ImprovedAtlanDocsCrawler:
    def __init__(self):
        self.base_url = "https://docs.atlan.com"
        self.visited_urls: Set[str] = set()
        self.url_data: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
    
    def crawl_documentation(self, max_pages: int = 100) -> List[Dict]:
        """Crawl Atlan documentation and extract URLs with metadata"""
        print(f"🚀 Starting crawl of {self.base_url}")
        
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
            "https://developer.atlan.com/sdks/python/",  # Specifically target Python SDK
            "https://developer.atlan.com/sdks/java/",
            "https://developer.atlan.com/sdks/go/",
            "https://developer.atlan.com/sdks/kotlin/",
            "https://developer.atlan.com/sdks/scala/"
        ]
        
        queue = seed_urls.copy()
        
        while queue and len(self.visited_urls) < max_pages:
            url = queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            try:
                print(f"📄 Crawling: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                self.visited_urls.add(url)
                
                # Extract page data with improved content extraction
                page_data = self.extract_page_data_improved(url, response.text)
                if page_data:
                    self.url_data.append(page_data)
                
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
        
        print(f"✅ Crawled {len(self.visited_urls)} pages")
        return self.url_data
    
    def extract_page_data_improved(self, url: str, html: str) -> Dict:
        """Extract relevant data from a page with improved content extraction"""
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
        
        # Extract headings
        headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        
        # Determine category and technology
        category = self.categorize_url(url, title_text, content_text)
        technology = self.extract_technology(url, title_text, content_text)
        
        return {
            "url": url,
            "title": title_text,
            "content": content_text,  # NO LENGTH LIMIT - extract full content
            "headings": headings,
            "category": category,
            "technology": technology,
            "path": urlparse(url).path
        }
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        # Remove leading/trailing whitespace
        content = content.strip()
        # Normalize spaces
        content = re.sub(r' +', ' ', content)
        return content
    
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
    
    def categorize_url(self, url: str, title: str, content: str) -> str:
        """Categorize URL based on path and content"""
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        if "sdk" in url_lower or "api" in url_lower or "developer" in url_lower:
            return "sdk"
        elif "connector" in url_lower or "integration" in url_lower:
            return "integrations"
        elif "governance" in url_lower or "policy" in url_lower or "glossary" in url_lower:
            return "governance"
        elif "how-to" in url_lower or "setup" in url_lower or "configure" in url_lower:
            return "how-to"
        else:
            return "general"
    
    def extract_technology(self, url: str, title: str, content: str) -> str:
        """Extract technology from URL and content"""
        text = f"{url} {title} {content}".lower()
        
        technologies = {
            "python": ["python", "py"],
            "java": ["java"],
            "javascript": ["javascript", "js", "node", "typescript"],
            "go": ["go", "golang"],
            "kotlin": ["kotlin"],
            "scala": ["scala"],
            "snowflake": ["snowflake"],
            "databricks": ["databricks"],
            "powerbi": ["powerbi", "power bi"],
            "tableau": ["tableau"],
            "mysql": ["mysql"],
            "postgres": ["postgres", "postgresql"],
            "mongodb": ["mongodb", "mongo"],
            "kafka": ["kafka"],
            "airflow": ["airflow"],
            "dbt": ["dbt"],
            "fivetran": ["fivetran"]
        }
        
        for tech, keywords in technologies.items():
            if any(keyword in text for keyword in keywords):
                return tech
        
        return "general"
    
    def save_to_file(self, filename: str = "improved_atlan_docs_data.json"):
        """Save crawled data to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.url_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(self.url_data)} pages to {filename}")

# Usage example
if __name__ == "__main__":
    crawler = ImprovedAtlanDocsCrawler()
    data = crawler.crawl_documentation(max_pages=50)
    crawler.save_to_file()
