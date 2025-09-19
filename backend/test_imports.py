#!/usr/bin/env python3
"""
Test script to isolate import issues
"""
import os
import sys

print("🔍 Testing imports step by step...")

try:
    print("1. Testing basic imports...")
    import openai
    print("   ✅ openai imported")
except Exception as e:
    print(f"   ❌ openai import failed: {e}")

try:
    print("2. Testing config import...")
    from config.settings import OPENAI_API_KEY, PINECONE_API_KEY
    print("   ✅ config imported")
    print(f"   �� OPENAI_API_KEY: {'SET' if OPENAI_API_KEY else 'NOT SET'}")
    print(f"   📋 PINECONE_API_KEY: {'SET' if PINECONE_API_KEY else 'NOT SET'}")
except Exception as e:
    print(f"   ❌ config import failed: {e}")

try:
    print("3. Testing Pinecone import...")
    from pinecone import Pinecone
    print("   ✅ Pinecone imported")
except Exception as e:
    print(f"   ❌ Pinecone import failed: {e}")

try:
    print("4. Testing crawler import...")
    from services.atlan_rag_crawler import atlan_rag_crawler
    print("   ✅ atlan_rag_crawler imported")
except Exception as e:
    print(f"   ❌ atlan_rag_crawler import failed: {e}")

try:
    print("5. Testing RAG service import...")
    from services.atlan_rag_service import atlan_rag_service
    print("   ✅ atlan_rag_service imported")
except Exception as e:
    print(f"   ❌ atlan_rag_service import failed: {e}")

try:
    print("6. Testing controllers import...")
    from controllers.rag_controller import router as rag_router
    print("   ✅ rag_controller imported")
except Exception as e:
    print(f"   ❌ rag_controller import failed: {e}")

try:
    print("7. Testing app import...")
    import app
    print("   ✅ app imported successfully!")
except Exception as e:
    print(f"   ❌ app import failed: {e}")

print("🎉 Import test completed!")
