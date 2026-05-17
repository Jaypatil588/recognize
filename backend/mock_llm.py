"""
Mock LLM responses for testing without API keys
Use this ONLY for UI testing, not for demo
"""

def mock_extract_entities(text: str) -> dict:
    """Return mock entities for testing"""
    return {
        "entities": [
            {"name": "Project Alpha", "type": "project", "description": "Main development project"},
            {"name": "John Smith", "type": "person", "description": "Project lead"},
            {"name": "Q3 Launch", "type": "event", "description": "Product launch scheduled for Q3"},
        ],
        "relationships": [
            {"source": "John Smith", "target": "Project Alpha", "type": "leads", "description": "John leads the project"},
            {"source": "Project Alpha", "target": "Q3 Launch", "type": "scheduled_for", "description": "Launch date set"},
        ]
    }

def mock_answer_query(query: str, context: str) -> str:
    """Return mock answer for testing"""
    return f"Based on the context, here's the answer to '{query}': [Mock response - replace with real API key for actual results]"
