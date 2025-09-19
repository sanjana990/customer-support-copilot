import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Pinecone API
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_TICKETS_INDEX = os.getenv("PINECONE_TICKETS_INDEX") 
PINECONE_DOCS_INDEX = os.getenv("PINECONE_DOCS_INDEX")   