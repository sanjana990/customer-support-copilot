import openai
import json
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def classify_ticket(ticket_content: str, ticket_subject: str = ""):
    """
    Classify a ticket using OpenAI to determine topic, sentiment, and priority
    """
    
    # Combine subject and body for analysis
    full_content = f"Subject: {ticket_subject}\n\nBody: {ticket_content}"
    
    # Define the classification prompt with the exact topic categories
    classification_prompt = f"""
    Analyze the following customer support ticket and classify it according to these criteria:

    TICKET CONTENT:
    {full_content}

    Please classify this ticket and respond with a JSON object containing:

    1. topic: One of these EXACT categories (choose the most appropriate):
       - "How-to" (Getting started, tutorials, step-by-step instructions, setup guides, "how do I", "how can I", "how to")
       - "Product" (Product features, capabilities, what Atlan can do, feature questions, product overview)
       - "Connector" (Data connectors, connecting data sources, third-party integrations, data ingestion)
       - "Lineage" (Data lineage, dependencies, flow tracking, data relationships, impact analysis)
       - "API/SDK" (API usage, SDK issues, authentication, endpoints, code examples, developer tools)
       - "SSO" (Single Sign-On, authentication, SAML, OAuth, identity management, login issues)
       - "Glossary" (Data glossary, business terms, definitions, metadata management, terminology)
       - "Best practices" (Recommended approaches, optimization tips, best practices, guidelines)
       - "Sensitive data" (Data privacy, security, compliance, sensitive data handling, PII, GDPR)
       - "General" (Only for non-Atlan related questions like cooking, weather, personal topics)

    2. sentiment: One of these (be more sensitive to emotional cues):
       - "Positive" (Satisfied, happy, grateful, excited, appreciative)
       - "Neutral" (Pure informational, matter-of-fact, no emotional indicators)
       - "Frustrated" (Annoyed, impatient, negative tone, mentions problems/failures, expresses difficulty)
       - "Urgent" (Critical, emergency, blocking, time-sensitive, "ASAP", "immediately")

    3. priority: One of these (consider business impact):
       - "P0" (Critical/Urgent - blocking production, security issues, system down, data loss)
       - "P1" (High - important features not working, significant business impact, user blocked)
       - "P2" (Medium - standard support requests, minor issues, informational questions)

    IMPORTANT GUIDELINES (PRIORITIZE TECHNOLOGY KEYWORDS):
    - If mentions "SDK", "API", "Python SDK", "Go SDK", "Java SDK", "JavaScript SDK", "Code", "Developer", "Authentication" → "API/SDK" topic (HIGHEST PRIORITY)
    - If mentions "Connect to", "Integrate with", "Data source", "Connector", "Snowflake", "Databricks", "PowerBI" → "Connector" topic
    - If mentions "Data flow", "Dependencies", "Impact", "Lineage" → "Lineage" topic
    - If mentions "Login", "SSO", "SAML", "OAuth", "Identity" → "SSO" topic
    - If mentions "Glossary", "Terms", "Definitions", "Metadata" → "Glossary" topic
    - If mentions "Best practice", "Optimize", "Recommend", "Guidelines" → "Best practices" topic
    - If mentions "Privacy", "Security", "Compliance", "Sensitive", "PII", "GDPR" → "Sensitive data" topic
    - If mentions "What can Atlan do", "What features", "What capabilities" → "Product" topic
    - Only if NO technology keywords mentioned: "How can I get started", "How do I set up", "How to use", "How to configure" → "How-to" topic
    - If someone mentions "failing", "not working", "error", "problem", "issue", "difficult", "sparse documentation" → likely Frustrated sentiment
    - If someone says "urgent", "ASAP", "blocking", "critical", "emergency" → likely Urgent sentiment and P0/P1 priority
    - If someone is asking "how to" or "best practices" without problems → likely Neutral sentiment and P2 priority
    - If someone expresses gratitude, satisfaction, or excitement → likely Positive sentiment
    - Only use "General" for clearly non-Atlan related topics (cooking, weather, personal, etc.)

    4. confidence: A number between 0.0 and 1.0 indicating classification confidence

    5. topic_reasoning: Specific explanation for why this topic was chosen
    6. sentiment_reasoning: Specific explanation for why this sentiment was chosen (mention specific words/phrases)
    7. priority_reasoning: Specific explanation for why this priority was chosen (consider business impact)

    Respond with ONLY a valid JSON object, no other text.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert customer support ticket classifier. Be sensitive to emotional cues and business impact. Always respond with valid JSON only."},
                {"role": "user", "content": classification_prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        # Parse the JSON response
        classification_text = response["choices"][0]["message"]["content"].strip()
        
        # Clean up the response (remove any markdown formatting)
        if classification_text.startswith("```json"):
            classification_text = classification_text[7:]
        if classification_text.endswith("```"):
            classification_text = classification_text[:-3]
        
        classification = json.loads(classification_text)
        
        # Validate and set defaults if needed
        return {
            "topic": classification.get("topic", "General"),
            "sentiment": classification.get("sentiment", "Neutral"),
            "priority": classification.get("priority", "P2"),
            "confidence": float(classification.get("confidence", 0.8)),
            "topic_reasoning": classification.get("topic_reasoning", "Auto-classified based on content analysis"),
            "sentiment_reasoning": classification.get("sentiment_reasoning", "Auto-classified based on tone analysis"),
            "priority_reasoning": classification.get("priority_reasoning", "Auto-classified based on urgency indicators")
        }
        
    except Exception as e:
        print(f"Classification error: {e}")
        # Return default classification if AI fails
        return {
            "topic": "General",
            "sentiment": "Neutral", 
            "priority": "P2",
            "confidence": 0.5,
            "topic_reasoning": f"Classification failed: {str(e)}",
            "sentiment_reasoning": f"Classification failed: {str(e)}",
            "priority_reasoning": f"Classification failed: {str(e)}"
        }
