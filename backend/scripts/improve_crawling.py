#!/usr/bin/env python3
"""
Script to improve crawling and update the documentation data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.improved_atlan_rag_crawler import ImprovedAtlanRAGCrawler
from services.improved_atlan_docs_crawler import ImprovedAtlanDocsCrawler

def main():
    print("🚀 Starting improved crawling process...")
    
    # Option 1: Update the JSON data file
    print("\n📄 Step 1: Updating JSON data with improved crawling...")
    docs_crawler = ImprovedAtlanDocsCrawler()
    data = docs_crawler.crawl_documentation(max_pages=50)
    docs_crawler.save_to_file("backend/improved_atlan_docs_data.json")
    
    # Option 2: Update Pinecone with improved crawling
    print("\n🔍 Step 2: Updating Pinecone with improved crawling...")
    rag_crawler = ImprovedAtlanRAGCrawler()
    success = rag_crawler.crawl_and_store(max_pages=50)
    
    if success:
        print("✅ Improved crawling completed successfully!")
        print("📊 Your system should now have detailed Python SDK content including:")
        print("   - pip install pyatlan commands")
        print("   - AsyncAtlanClient examples")
        print("   - Environment variable configuration")
        print("   - Code examples and usage patterns")
        print("   - Advanced features like concurrent operations")
    else:
        print("❌ Improved crawling failed. Check the logs for details.")

if __name__ == "__main__":
    main()
