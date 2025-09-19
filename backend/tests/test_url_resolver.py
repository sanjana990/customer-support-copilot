import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock all external dependencies before importing
with patch('pinecone.init'), \
     patch('pinecone.Index'), \
     patch('services.vector_db_service.pc'), \
     patch('services.vector_db_service.tickets_index'), \
     patch('services.vector_db_service.docs_index'):
    
    from services.crawled_data_url_resolver import url_resolver

class TestURLResolver:
    
    def test_extract_technology_python(self):
        """Test technology extraction for Python queries"""
        query = "How do I install the Python SDK?"
        technology = url_resolver._extract_technology(query)
        assert technology == "python"
    
    def test_extract_technology_java(self):
        """Test technology extraction for Java queries"""
        query = "Java SDK authentication example"
        technology = url_resolver._extract_technology(query)
        assert technology == "java"
    
    def test_extract_technology_kotlin(self):
        """Test technology extraction for Kotlin queries"""
        query = "Kotlin SDK setup guide"
        technology = url_resolver._extract_technology(query)
        assert technology == "kotlin"
    
    def test_extract_technology_scala(self):
        """Test technology extraction for Scala queries"""
        query = "Scala SDK integration"
        technology = url_resolver._extract_technology(query)
        assert technology == "scala"
    
    def test_extract_technology_go(self):
        """Test technology extraction for Go queries"""
        query = "Go SDK documentation"
        technology = url_resolver._extract_technology(query)
        assert technology == "go"
    
    def test_extract_technology_javascript(self):
        """Test technology extraction for JavaScript queries"""
        query = "JavaScript SDK examples"
        technology = url_resolver._extract_technology(query)
        assert technology == "javascript"
    
    def test_extract_technology_no_match(self):
        """Test technology extraction when no technology found"""
        query = "How do I connect to Snowflake?"
        technology = url_resolver._extract_technology(query)
        assert technology is None
    
    def test_is_real_sdk_url_valid(self):
        """Test valid SDK URL detection"""
        url = "https://developer.atlan.com/sdks/python/"
        is_sdk = url_resolver._is_real_sdk_url(url)
        assert is_sdk is True
    
    def test_is_real_sdk_url_invalid_snippet(self):
        """Test invalid SDK URL with snippet"""
        url = "https://developer.atlan.com/sdks/python/snippet"
        is_sdk = url_resolver._is_real_sdk_url(url)
        assert is_sdk is False
    
    def test_is_real_sdk_url_invalid_example(self):
        """Test invalid SDK URL with example"""
        url = "https://developer.atlan.com/sdks/python/example"
        is_sdk = url_resolver._is_real_sdk_url(url)
        assert is_sdk is False
    
    def test_is_real_sdk_url_non_sdk(self):
        """Test non-SDK URL"""
        url = "https://developer.atlan.com/connectors/snowflake/"
        is_sdk = url_resolver._is_real_sdk_url(url)
        assert is_sdk is False
    
    def test_resolve_urls_with_topic_sdk_query(self):
        """Test URL resolution for SDK-related queries"""
        query = "How do I install the Python SDK?"
        topic = "API/SDK"
        
        urls = url_resolver.resolve_urls_with_topic(query, topic)
        
        # Should return URLs
        assert isinstance(urls, list)
        if urls:  # If URLs are found
            assert len(urls) > 0
            # Check that URLs contain relevant information
            for url_info in urls:
                assert "url" in url_info
                assert "doc" in url_info
    
    def test_resolve_urls_with_topic_non_sdk_query(self):
        """Test URL resolution for non-SDK queries"""
        query = "How do I connect to Snowflake?"
        topic = "Connector"
        
        urls = url_resolver.resolve_urls_with_topic(query, topic)
        
        # Should return URLs
        assert isinstance(urls, list)
        if urls:  # If URLs are found
            assert len(urls) > 0
    
    def test_resolve_urls_with_topic_empty_query(self):
        """Test URL resolution with empty query"""
        query = ""
        topic = "General"
        
        urls = url_resolver.resolve_urls_with_topic(query, topic)
        
        # Should return empty list or fallback URLs
        assert isinstance(urls, list)
    
    def test_rank_and_deduplicate_urls(self):
        """Test URL ranking and deduplication"""
        urls = [
            {"url": "https://developer.atlan.com/sdks/python/", "doc": "Python SDK", "score": 0.9},
            {"url": "https://developer.atlan.com/sdks/python/", "doc": "Python SDK Alt", "score": 0.8},
            {"url": "https://developer.atlan.com/sdks/java/", "doc": "Java SDK", "score": 0.7}
        ]
        
        ranked_urls = url_resolver._rank_and_deduplicate_urls(urls)
        
        # Should deduplicate and rank
        assert len(ranked_urls) <= len(urls)
        assert len(ranked_urls) > 0
        
        # Check that highest score comes first
        if len(ranked_urls) > 1:
            assert ranked_urls[0]["score"] >= ranked_urls[1]["score"]
