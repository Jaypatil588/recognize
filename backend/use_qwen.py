"""
Quick patch to use Qwen Cloud instead of Claude
For hackathon - uses free Qwen credits instead of paid Anthropic
"""

import os
from openai import OpenAI

# Qwen Cloud uses OpenAI-compatible API
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY", ""),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def qwen_extract_entities(text: str) -> dict:
    """
    Extract entities using Qwen instead of Claude
    """
    prompt = f"""Extract entities and relationships from this text.

Text: {text}

Return JSON with:
{{
    "entities": [
        {{"name": "...", "type": "person|organization|concept|event", "description": "..."}}
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "...", "description": "..."}}
    ]
}}"""

    try:
        response = client.chat.completions.create(
            model="qwen-plus",  # or "qwen-turbo" for faster/cheaper
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured information from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON from response
        import json
        if "```json" in result:
            json_str = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            json_str = result.split("```")[1].split("```")[0].strip()
        else:
            json_str = result
        
        return json.loads(json_str)
    
    except Exception as e:
        print(f"Qwen API error: {e}")
        return {"entities": [], "relationships": []}


def qwen_answer_query(query: str, context: str) -> str:
    """
    Answer query using Qwen instead of Claude
    """
    prompt = f"""Answer this question using the provided context.

Question: {query}

Context:
{context}

Provide a clear, concise answer with citations."""

    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Qwen API error: {e}")
        return f"Error generating answer: {e}"


# Usage in your main.py:
# Replace Claude calls with:
# from use_qwen import qwen_extract_entities, qwen_answer_query
# entities = qwen_extract_entities(text)
# answer = qwen_answer_query(query, context)
