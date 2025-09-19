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
    
    from services.atlan_rag_service import AtlanRAGService

class TestAtlanRAGService:
    
    @pytest.fixture
    def rag_service(self):
        return AtlanRAGService()
    
    @pytest.mark.asyncio
    async def test_generate_rag_response_success(self, rag_service):
        """Test successful RAG response generation"""
        with patch.object(rag_service.crawler, 'index', True), \
             patch.object(rag_service.crawler, 'search_content') as mock_search:
            
            # Mock search results
            mock_search.return_value = [
                {
                    'id': 'doc1',
                    'score': 0.95,
                    'metadata': {
                        'content': 'To install the Python SDK, use pip install atlan-python-sdk',
                        'url': 'https://developer.atlan.com/sdks/python/',
                        'title': 'Python SDK Installation'
                    }
                }
            ]
            
            with patch('services.atlan_rag_service.openai.ChatCompletion.create') as mock_openai:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "To install the Python SDK, use pip install atlan-python-sdk"
                mock_openai.return_value = mock_response
                
                result = await rag_service.generate_rag_response("How do I install the Python SDK?")
                
                assert "answer" in result
                assert "citations" in result
                assert "sources" in result
                assert "Python SDK" in result["answer"]
                assert len(result["citations"]) > 0
                assert "developer.atlan.com" in result["citations"][0]["url"]
    
    @pytest.mark.asyncio
    async def test_generate_rag_response_no_results(self, rag_service):
        """Test RAG response when no search results found"""
        with patch.object(rag_service.crawler, 'index', True), \
             patch.object(rag_service.crawler, 'search_content') as mock_search:
            
            # Mock empty search results
            mock_search.return_value = []
            
            result = await rag_service.generate_rag_response("Random unrelated query")
            
            assert "answer" in result
            assert "citations" in result
            assert "sources" in result
            assert "couldn't find relevant information" in result["answer"]
            assert len(result["citations"]) == 0
            assert len(result["sources"]) == 0
    
    @pytest.mark.asyncio
    async def test_generate_rag_response_setup_pinecone(self, rag_service):
        """Test RAG response when Pinecone needs setup"""
        with patch.object(rag_service.crawler, 'index', None), \
             patch.object(rag_service.crawler, 'setup_pinecone_index') as mock_setup, \
             patch.object(rag_service.crawler, 'search_content') as mock_search:
            
            # Mock search results
            mock_search.return_value = [
                {
                    'id': 'doc1',
                    'score': 0.95,
                    'metadata': {
                        'content': 'Test content',
                        'url': 'https://test.com',
                        'title': 'Test Title'
                    }
                }
            ]
            
            with patch('services.atlan_rag_service.openai.ChatCompletion.create') as mock_openai:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Test answer"
                mock_openai.return_value = mock_response
                
                result = await rag_service.generate_rag_response("Test query")
                
                # Verify setup was called
                mock_setup.assert_called_once()
                assert "answer" in result
                assert "Test answer" in result["answer"]
    
    @pytest.mark.asyncio
    async def test_generate_rag_response_deduplication(self, rag_service):
        """Test RAG response with URL deduplication"""
        with patch.object(rag_service.crawler, 'index', True), \
             patch.object(rag_service.crawler, 'search_content') as mock_search:
            
            # Mock search results with duplicate URLs
            mock_search.return_value = [
                {
                    'id': 'doc1',
                    'score': 0.95,
                    'metadata': {
                        'content': 'Content 1',
                        'url': 'https://developer.atlan.com/sdks/python/',
                        'title': 'Python SDK'
                    }
                },
                {
                    'id': 'doc2',
                    'score': 0.90,
                    'metadata': {
                        'content': 'Content 2',
                        'url': 'https://developer.atlan.com/sdks/python/',
                        'title': 'Python SDK Alternative'
                    }
                }
            ]
            
            with patch('services.atlan_rag_service.openai.ChatCompletion.create') as mock_openai:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Test answer"
                mock_openai.return_value = mock_response
                
                result = await rag_service.generate_rag_response("Test query")
                
                # Should deduplicate URLs
                unique_urls = set(citation["url"] for citation in result["citations"])
                assert len(unique_urls) == 1
                assert "developer.atlan.com" in list(unique_urls)[0]
    
    @pytest.mark.asyncio
    async def test_generate_rag_response_openai_error(self, rag_service):
        """Test RAG response when OpenAI API fails"""
        with patch.object(rag_service.crawler, 'index', True), \
             patch.object(rag_service.crawler, 'search_content') as mock_search:
            
            # Mock search results
            mock_search.return_value = [
                {
                    'id': 'doc1',
                    'score': 0.95,
                    'metadata': {
                        'content': 'Test content',
                        'url': 'https://test.com',
                        'title': 'Test Title'
                    }
                }
            ]
            
            with patch('services.atlan_rag_service.openai.ChatCompletion.create') as mock_openai:
                # Mock OpenAI API error
                mock_openai.side_effect = Exception("OpenAI API Error")
                
                result = await rag_service.generate_rag_response("Test query")
                
                # Should handle error gracefully
                assert "answer" in result
                assert "error" in result["answer"].lower() or "sorry" in result["answer"].lower()
