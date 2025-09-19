import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def generate_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response["data"][0]["embedding"]

async def generate_response(query: str, context: str):
    # Create a more detailed prompt that asks for comprehensive answers with proper formatting
    prompt = f"""You are an expert Atlan customer support assistant. Based on the following context and user query, provide a comprehensive, helpful answer with proper formatting.

Context: {context}

User Query: {query}

Please provide a detailed response that:
1. Directly answers the user's question with specific steps or explanations
2. Includes relevant technical details when appropriate
3. Provides actionable guidance
4. Is clear and easy to follow
5. Formats code snippets properly with clear language indicators (e.g., ```python, ```bash, ```json)
6. Uses proper markdown formatting for lists, headers, and emphasis
7. Provides step-by-step instructions when applicable

Do not just provide URLs or ask users to visit links. Give them the actual information they need in your response.

Format your response with:
- Clear headings using ## or ###
- Numbered or bulleted lists for steps
- Code blocks with proper syntax highlighting
- Bold text for important points
- Clear section breaks

Answer:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful Atlan customer support assistant. Provide detailed, actionable answers based on the given context. Use proper markdown formatting with code blocks, lists, and clear structure. Do not just provide URLs - give comprehensive responses with actual information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.3
    )
    return response["choices"][0]["message"]["content"].strip()
