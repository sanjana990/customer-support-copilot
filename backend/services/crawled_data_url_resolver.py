import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class URLResult:
    doc: str
    url: str
    relevance_score: float
    is_valid: bool

class CrawledDataURLResolver:
    def __init__(self, data_file: str = "atlan_docs_data_extended.json"):
        self.data_file = data_file
        self.crawled_data = self._load_crawled_data()
        self.intent_keywords = {
            'setup': ['setup', 'install', 'configure', 'connect', 'integrate', 'getting started'],
            'authentication': ['auth', 'authenticate', 'login', 'api key', 'token', 'sso'],
            'lineage': ['lineage', 'data flow', 'provenance'],
            'permissions': ['permissions', 'access control', 'rbac', 'roles'],
            'governance': ['governance', 'policy', 'compliance', 'security', 'pii'],
            'troubleshoot': ['error', 'fail', 'issue', 'debug', 'troubleshoot'],
            'example': ['example', 'how to', 'guide', 'tutorial'],
            'general': []
        }
    
    def _load_crawled_data(self) -> List[Dict]:
        """Load the crawled documentation data"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.data_file} not found. Using fallback URLs.")
            return []
    
    def resolve_urls_with_topic(self, classified_topic: str, query: str) -> List[URLResult]:
        """Resolves URLs using crawled data and classified topic"""
        print(f"DEBUG: CrawledDataURLResolver - topic='{classified_topic}', query='{query}'")
        
        # Extract intent from query
        intent = self._extract_intent(query)
        technology = self._extract_technology(query)
        
        # Find matching URLs from crawled data
        candidates = self._find_matching_urls(classified_topic, intent, technology, query)
        
        # Rank and return top results with deduplication
        ranked_urls = self._rank_and_deduplicate_urls(candidates, intent, technology)
        return ranked_urls[:3]
    
    def _extract_intent(self, query: str) -> str:
        """Extract intent from query"""
        query_lower = query.lower()
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        return 'general'
    
    def _extract_technology(self, query: str) -> Optional[str]:
        """Extract technology from query with enhanced patterns"""
        query_lower = query.lower()
        tech_patterns = {
            'python': ['python', 'py'],
            'java': ['java', 'jdk', 'jvm'],
            'javascript': ['javascript', 'js', 'node', 'nodejs', 'typescript', 'ts'],
            'go': ['go', 'golang'],
            'scala': ['scala'],
            'kotlin': ['kotlin', 'kt'],
            'csharp': ['c#', 'csharp', 'dotnet', '.net'],
            'php': ['php'],
            'ruby': ['ruby', 'rb'],
            'rust': ['rust', 'rs'],
            'snowflake': ['snowflake'],
            'databricks': ['databricks'],
            'powerbi': ['powerbi', 'power bi'],
            'tableau': ['tableau'],
            'looker': ['looker'],
            'dbt': ['dbt', 'data build tool'],
            'airflow': ['airflow'],
            'kafka': ['kafka'],
            'mongodb': ['mongodb', 'mongo'],
            'postgres': ['postgres', 'postgresql'],
            'mysql': ['mysql'],
            'bigquery': ['bigquery'],
            'redshift': ['redshift'],
            'athena': ['athena'],
            's3': ['s3', 'aws s3'],
            'azure': ['azure'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform']
        }
        
        # Check for exact matches first (higher priority)
        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    # Additional check to avoid false positives
                    if tech == 'java' and any(other_tech in query_lower for other_tech in ['javascript', 'scala', 'kotlin']):
                        continue  # Skip java if more specific tech is mentioned
                    return tech
        return None
    
    def _find_matching_urls(self, topic: str, intent: str, technology: Optional[str], query: str) -> List[URLResult]:
        """Find URLs from crawled data that match the query"""
        candidates = []
        query_lower = query.lower()
        
        print(f"DEBUG: Finding URLs - topic={topic}, intent={intent}, technology={technology}")
        
        for item in self.crawled_data:
            url = item['url']
            title = item['title']
            content = item['content']
            category = item['category']
            tech = item['technology']
            
            # Calculate relevance score
            score = 0.0
            
            # Topic matching
            if topic.lower() in ['connector', 'integrations'] and category == 'integrations':
                score += 0.8
            elif topic.lower() in ['api/sdk'] and category == 'sdk':
                score += 0.8
            elif topic.lower() in ['governance', 'glossary'] and category == 'governance':
                score += 0.8
            elif topic.lower() in ['how-to'] and category in ['how-to', 'integrations', 'sdk']:
                score += 0.7
            
            # Technology matching (most important for SDK questions)
            if technology and tech == technology:
                score += 0.9
            elif technology and technology in url.lower():
                score += 0.8
            elif technology and technology in title.lower():
                score += 0.7
            elif technology and technology in content.lower():
                score += 0.5
            
            # Intent matching
            if intent == 'setup' and 'setup' in url.lower():
                score += 0.9
            elif intent == 'setup' and 'how-tos' in url.lower():
                score += 0.8
            elif intent == 'authentication' and 'auth' in url.lower():
                score += 0.8
            
            # Query keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if word in url.lower():
                    score += 0.3
                if word in title.lower():
                    score += 0.2
                if word in content.lower():
                    score += 0.1
            
            # Only include URLs with reasonable relevance
            if score > 0.3:
                candidates.append(URLResult(
                    doc=title or f"{tech.title()} Documentation",
                    url=url,
                    relevance_score=score,
                    is_valid=True
                ))
                print(f"DEBUG: Added candidate - {tech} - {url} - score={score:.2f}")
        
        return candidates
    
    def _rank_and_deduplicate_urls(self, candidates: List[URLResult], intent: str, technology: Optional[str]) -> List[URLResult]:
        """Rank URLs by relevance and remove duplicates"""
        # Sort by relevance score (higher is better)
        ranked_urls = sorted(candidates, key=lambda x: x.relevance_score, reverse=True)
        
        # Remove duplicates based on URL
        seen_urls = set()
        deduplicated = []
        
        for url_result in ranked_urls:
            if url_result.url not in seen_urls:
                seen_urls.add(url_result.url)
                deduplicated.append(url_result)
        
        # If we don't have enough results and technology was specified, add fallback URLs
        if len(deduplicated) < 3 and technology:
            fallback_urls = self._get_technology_fallback_urls(technology)
            for fallback in fallback_urls:
                if fallback.url not in seen_urls:
                    deduplicated.append(fallback)
                    seen_urls.add(fallback.url)
        
        return deduplicated
    
    def _get_technology_fallback_urls(self, technology: str) -> List[URLResult]:
        """Get fallback URLs for specific technologies when not found in crawled data"""
        fallback_urls = {
            'scala': [
                URLResult("Scala SDK Documentation", "https://docs.atlan.com/develop/sdk/scala", 0.8, True),
                URLResult("Atlan Scala SDK", "https://developer.atlan.com/sdk/scala", 0.7, True)
            ],
            'kotlin': [
                URLResult("Kotlin SDK Documentation", "https://docs.atlan.com/develop/sdk/kotlin", 0.8, True),
                URLResult("Atlan Kotlin SDK", "https://developer.atlan.com/sdk/kotlin", 0.7, True)
            ],
            'java': [
                URLResult("Java SDK Documentation", "https://docs.atlan.com/develop/sdk/java", 0.8, True),
                URLResult("Atlan Java SDK", "https://developer.atlan.com/sdk/java", 0.7, True)
            ],
            'csharp': [
                URLResult("C# SDK Documentation", "https://docs.atlan.com/develop/sdk/csharp", 0.8, True),
                URLResult("Atlan .NET SDK", "https://developer.atlan.com/sdk/csharp", 0.7, True)
            ]
        }
        
        return fallback_urls.get(technology, [
            URLResult(f"{technology.title()} SDK Documentation", f"https://docs.atlan.com/develop/sdk/{technology}", 0.6, True),
            URLResult("Atlan Developer Hub", "https://developer.atlan.com", 0.5, True)
        ])

# Global instance
url_resolver = CrawledDataURLResolver()
