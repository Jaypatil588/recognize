"""
Groq API Integration for Context Graph
Ultra-fast inference with Llama models
"""

import os
import json
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

def groq_extract_entities(text: str) -> dict:
    """
    Extract entities and relationships using Groq (Llama 3)
    
    Args:
        text: Text to analyze
        
    Returns:
        dict with entities and relationships
    """
    prompt = f"""Extract entities and relationships from this text.

Text: {text}

Return ONLY valid JSON in this exact format:
{{
    "entities": [
        {{"name": "entity name", "type": "person|organization|concept|event", "description": "brief description"}}
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "relationship type", "description": "brief description"}}
    ]
}}

Important: Return ONLY the JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and accurate
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured information from text. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON from response
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result.strip()
        
        return json.loads(json_str)
    
    except Exception as e:
        print(f"Groq API error: {e}")
        return {"entities": [], "relationships": []}


def groq_answer_query(query: str, context: str) -> str:
    """
    Answer query using Groq with GraphRAG context
    
    Args:
        query: User question
        context: Retrieved context from graph
        
    Returns:
        Answer string
    """
    prompt = f"""Answer this question using the provided context from our knowledge graph.

Question: {query}

Context:
{context}

Provide a clear, concise answer with specific citations to entities mentioned in the context."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"Error generating answer: {e}"


def groq_summarize_text(text: str) -> str:
    """
    Summarize text using Groq
    
    Args:
        text: Text to summarize
        
    Returns:
        Summary string
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating concise, informative summaries."
                },
                {
                    "role": "user",
                    "content": f"Summarize this text in 2-3 sentences:\n\n{text}"
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Groq API error: {e}")
        return ""


# Test function
def test_groq_connection():
    """Test if Groq API is working"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Groq is working!'"}
            ],
            max_tokens=10
        )
        print(f"✅ Groq API working: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Groq API connection...")
    test_groq_connection()
