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
    
    from fastapi.testclient import TestClient
    from app import app

client = TestClient(app)

class TestRAGController:
    
    def test_rag_query_success(self):
        """Test successful RAG query"""
        with patch('controllers.rag_controller.classify_ticket') as mock_classify, \
             patch('controllers.rag_controller.atlan_rag_service') as mock_rag:
            
            # Mock classification
            mock_classify.return_value = {
                "topic": "API/SDK",
                "sentiment": "Neutral",
                "priority": "P2",
                "confidence": 0.9,
                "topic_reasoning": "SDK related query",
                "sentiment_reasoning": "Neutral tone",
                "priority_reasoning": "Standard priority"
            }
            
            # Mock RAG service
            mock_rag.generate_rag_response.return_value = {
                "answer": "To install the Python SDK, use pip install atlan-python-sdk",
                "citations": [{"url": "https://developer.atlan.com/sdks/python/", "doc": "Python SDK Docs"}],
                "sources": ["python-sdk-docs"]
            }
            
            response = client.post("/api/rag/query", json={
                "query": "How do I install the Python SDK?",
                "channel": "Web Chat",
                "session_id": "test-session",
                "include_followup": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "citations" in data
            assert "classification" in data
            assert data["classification"]["topic"] == "API/SDK"
            assert "Python SDK" in data["answer"]
    
    def test_rag_query_routing_message(self):
        """Test RAG query that gets routed instead of answered"""
        with patch('controllers.rag_controller.classify_ticket') as mock_classify:
            
            # Mock classification for non-RAG topic
            mock_classify.return_value = {
                "topic": "Connector",
                "sentiment": "Neutral",
                "priority": "P2",
                "confidence": 0.8,
                "topic_reasoning": "Connector related query",
                "sentiment_reasoning": "Neutral tone",
                "priority_reasoning": "Standard priority"
            }
            
            response = client.post("/api/rag/query", json={
                "query": "How do I connect to Snowflake?",
                "channel": "Web Chat",
                "session_id": "test-session",
                "include_followup": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "routing" in data["answer"].lower()
            assert data["classification"]["topic"] == "Connector"
            assert data["response_type"] == "routing_message"
    
    def test_rag_query_non_atlan_related(self):
        """Test query that's not Atlan-related"""
        with patch('controllers.rag_controller.classify_ticket') as mock_classify:
            
            # Mock classification for non-Atlan topic
            mock_classify.return_value = {
                "topic": "General",
                "sentiment": "Neutral",
                "priority": "P3",
                "confidence": 0.9,
                "topic_reasoning": "Cooking question, not Atlan related",
                "sentiment_reasoning": "Neutral tone",
                "priority_reasoning": "Low priority"
            }
            
            response = client.post("/api/rag/query", json={
                "query": "How do I make pasta?",
                "channel": "Web Chat",
                "session_id": "test-session",
                "include_followup": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "only help with Atlan" in data["answer"]
            assert data["classification"]["topic"] == "General"
    
    def test_rag_query_missing_fields(self):
        """Test RAG query with missing required fields"""
        response = client.post("/api/rag/query", json={
            "query": "Test query"
            # Missing channel, session_id, include_followup
        })
        
        assert response.status_code == 200  # Should still work with defaults
    
    def test_rag_query_invalid_json(self):
        """Test RAG query with invalid JSON"""
        response = client.post("/api/rag/query", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422  # Validation error
    
    def test_rag_query_empty_query(self):
        """Test RAG query with empty query"""
        with patch('controllers.rag_controller.classify_ticket') as mock_classify:
            
            mock_classify.return_value = {
                "topic": "General",
                "sentiment": "Neutral",
                "priority": "P3",
                "confidence": 0.1,
                "topic_reasoning": "Empty query",
                "sentiment_reasoning": "No content",
                "priority_reasoning": "Low priority"
            }
            
            response = client.post("/api/rag/query", json={
                "query": "",
                "channel": "Web Chat",
                "session_id": "test-session",
                "include_followup": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["classification"]["confidence"] == 0.1
