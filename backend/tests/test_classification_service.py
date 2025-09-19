import pytest
import asyncio
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
    
    from services.classification_service import classify_ticket

class TestClassificationService:
    
    @pytest.mark.asyncio
    async def test_classify_ticket_api_sdk(self):
        """Test classification of API/SDK related tickets"""
        with patch('services.classification_service.openai.ChatCompletion.create') as mock_openai:
            # Mock OpenAI response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "topic": "API/SDK",
                "sentiment": "Neutral",
                "priority": "P2",
                "confidence": 0.9,
                "topic_reasoning": "User is asking about Python SDK installation",
                "sentiment_reasoning": "Neutral tone, informational question",
                "priority_reasoning": "Standard support request"
            }
            '''
            mock_openai.return_value = mock_response
            
            result = await classify_ticket("How do I install the Python SDK?", "SDK Installation")
            
            assert result["topic"] == "API/SDK"
            assert result["sentiment"] == "Neutral"
            assert result["priority"] == "P2"
            assert result["confidence"] == 0.9
            assert "Python SDK" in result["topic_reasoning"]
    
    @pytest.mark.asyncio
    async def test_classify_ticket_frustrated_sentiment(self):
        """Test classification of frustrated user tickets"""
        with patch('services.classification_service.openai.ChatCompletion.create') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "topic": "Connector",
                "sentiment": "Frustrated",
                "priority": "P1",
                "confidence": 0.85,
                "topic_reasoning": "User having issues with Snowflake connector",
                "sentiment_reasoning": "Expresses frustration with failing connection",
                "priority_reasoning": "High priority due to blocking issue"
            }
            '''
            mock_openai.return_value = mock_response
            
            result = await classify_ticket("Snowflake connector keeps failing and I'm frustrated!", "Connector Issue")
            
            assert result["topic"] == "Connector"
            assert result["sentiment"] == "Frustrated"
            assert result["priority"] == "P1"
            assert "frustration" in result["sentiment_reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_classify_ticket_urgent_priority(self):
        """Test classification of urgent tickets"""
        with patch('services.classification_service.openai.ChatCompletion.create') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "topic": "SSO",
                "sentiment": "Urgent",
                "priority": "P0",
                "confidence": 0.95,
                "topic_reasoning": "Critical SSO authentication issue",
                "sentiment_reasoning": "Urgent tone, blocking production",
                "priority_reasoning": "P0 - blocking production system"
            }
            '''
            mock_openai.return_value = mock_response
            
            result = await classify_ticket("URGENT: SSO is down, blocking all users!", "Critical SSO Issue")
            
            assert result["topic"] == "SSO"
            assert result["sentiment"] == "Urgent"
            assert result["priority"] == "P0"
            assert "urgent" in result["sentiment_reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_classify_ticket_general_topic(self):
        """Test classification of non-Atlan related tickets"""
        with patch('services.classification_service.openai.ChatCompletion.create') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "topic": "General",
                "sentiment": "Neutral",
                "priority": "P3",
                "confidence": 0.8,
                "topic_reasoning": "Question about cooking, not Atlan related",
                "sentiment_reasoning": "Neutral informational tone",
                "priority_reasoning": "Low priority, not Atlan related"
            }
            '''
            mock_openai.return_value = mock_response
            
            result = await classify_ticket("How do I make pasta?", "Cooking Question")
            
            assert result["topic"] == "General"
            assert result["sentiment"] == "Neutral"
            assert result["priority"] == "P3"
            assert "cooking" in result["topic_reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_classify_ticket_empty_content(self):
        """Test classification with empty content"""
        with patch('services.classification_service.openai.ChatCompletion.create') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "topic": "General",
                "sentiment": "Neutral",
                "priority": "P3",
                "confidence": 0.1,
                "topic_reasoning": "Empty content, cannot classify",
                "sentiment_reasoning": "No content to analyze",
                "priority_reasoning": "Low priority due to lack of information"
            }
            '''
            mock_openai.return_value = mock_response
            
            result = await classify_ticket("", "")
            
            assert result["topic"] == "General"
            assert result["confidence"] == 0.1
            assert "empty" in result["topic_reasoning"].lower()
