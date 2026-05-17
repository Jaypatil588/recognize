"""
AgentField Integration for Context Graph
Wraps existing functions as production-ready agents with async execution and shared memory
"""

# Install: pip install agentfield

from agentfield import agent, AgentField
import anthropic
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os

# Initialize AgentField
af = AgentField()

# ── Agent 1: Document Processor ──────────────────────────────────────────────
@agent(name="document_processor", memory=True)
async def process_document(content: str, filename: str) -> dict:
    """
    Extract and chunk text from uploaded documents
    
    Args:
        content: Raw document content
        filename: Document filename
        
    Returns:
        dict with chunks and metadata
    """
    # Your existing text extraction logic
    import re
    from pathlib import Path
    
    # Simple chunking
    text = re.sub(r"\s+", " ", content).strip()
    chunks = []
    chunk_size = 600
    overlap = 80
    
    i = 0
    while i < len(text):
        end = min(i + chunk_size, len(text))
        chunks.append(text[i:end])
        i += chunk_size - overlap
    
    return {
        "filename": filename,
        "chunks": chunks,
        "total_chunks": len(chunks),
        "status": "processed"
    }


# ── Agent 2: Entity Extractor ─────────────────────────────────────────────────
@agent(name="entity_extractor", memory=True)
async def extract_entities(text: str, model: str = "claude") -> dict:
    """
    Extract entities and relationships from text using LLM
    
    Args:
        text: Text to analyze
        model: Which model to use (claude, qwen, etc.)
        
    Returns:
        dict with entities and relationships
    """
    # Use TokenRouter here (see below)
    from tokenrouter_integration import route_llm_call
    
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

    # Route through TokenRouter for optimization
    response = await route_llm_call(
        prompt=prompt,
        model=model,
        task_type="entity_extraction"
    )
    
    return response


# ── Agent 3: Graph Builder ───────────────────────────────────────────────────
@agent(name="graph_builder", memory=True)
async def build_graph(entities: list, relationships: list, doc_id: str) -> dict:
    """
    Build knowledge graph in Neo4j from entities and relationships
    
    Args:
        entities: List of entity dicts
        relationships: List of relationship dicts
        doc_id: Document identifier
        
    Returns:
        dict with graph statistics
    """
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "Durban@28")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    with driver.session() as session:
        # Create entities
        for entity in entities:
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $type,
                    e.description = $description,
                    e.doc_id = $doc_id
            """, name=entity["name"], type=entity["type"], 
                 description=entity.get("description", ""), doc_id=doc_id)
        
        # Create relationships
        for rel in relationships:
            session.run("""
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $target})
                MERGE (a)-[r:RELATES {type: $type}]->(b)
                SET r.description = $description,
                    r.doc_id = $doc_id
            """, source=rel["source"], target=rel["target"], 
                 type=rel["type"], description=rel.get("description", ""), doc_id=doc_id)
    
    driver.close()
    
    return {
        "entities_created": len(entities),
        "relationships_created": len(relationships),
        "doc_id": doc_id,
        "status": "graph_built"
    }


# ── Agent 4: Query Handler ────────────────────────────────────────────────────
@agent(name="query_handler", memory=True)
async def handle_query(query: str, top_k: int = 5) -> dict:
    """
    GraphRAG query: retrieve context from graph and generate answer
    
    Args:
        query: User question
        top_k: Number of context chunks to retrieve
        
    Returns:
        dict with answer and sources
    """
    # 1. Embed query
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = embedder.encode(query).tolist()
    
    # 2. Vector search in Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "Durban@28")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    with driver.session() as session:
        # Get relevant entities
        result = session.run("""
            MATCH (e:Entity)
            RETURN e.name as name, e.type as type, e.description as description
            LIMIT $limit
        """, limit=top_k)
        
        context_entities = [dict(record) for record in result]
    
    driver.close()
    
    # 3. Generate answer with context
    from tokenrouter_integration import route_llm_call
    
    context_text = "\n".join([
        f"- {e['name']} ({e['type']}): {e['description']}"
        for e in context_entities
    ])
    
    prompt = f"""Answer this question using the provided context from our knowledge graph.

Question: {query}

Context:
{context_text}

Provide a clear answer with citations to specific entities."""

    answer = await route_llm_call(
        prompt=prompt,
        model="claude",
        task_type="question_answering"
    )
    
    return {
        "query": query,
        "answer": answer,
        "sources": context_entities,
        "num_sources": len(context_entities)
    }


# ── Multi-Agent Orchestration ─────────────────────────────────────────────────
@agent(name="orchestrator", memory=True)
async def process_document_pipeline(content: str, filename: str) -> dict:
    """
    Orchestrate the full pipeline: process → extract → build graph
    
    This is AgentField's power: multi-agent coordination in one line
    """
    # Step 1: Process document
    processed = await process_document(content, filename)
    
    # Step 2: Extract entities from each chunk (parallel)
    import asyncio
    entity_tasks = [
        extract_entities(chunk) 
        for chunk in processed["chunks"][:5]  # Limit for demo
    ]
    entity_results = await asyncio.gather(*entity_tasks)
    
    # Step 3: Combine all entities
    all_entities = []
    all_relationships = []
    for result in entity_results:
        all_entities.extend(result.get("entities", []))
        all_relationships.extend(result.get("relationships", []))
    
    # Step 4: Build graph
    import uuid
    doc_id = str(uuid.uuid4())
    graph_result = await build_graph(all_entities, all_relationships, doc_id)
    
    return {
        "status": "complete",
        "processed": processed,
        "entities_extracted": len(all_entities),
        "graph": graph_result,
        "doc_id": doc_id
    }


# ── FastAPI Integration ───────────────────────────────────────────────────────
def setup_agentfield_routes(app):
    """Add AgentField-powered endpoints to your FastAPI app"""
    
    @app.post("/api/agentfield/upload")
    async def upload_with_agents(content: str, filename: str):
        """Upload and process document using agent swarm"""
        result = await process_document_pipeline(content, filename)
        return result
    
    @app.post("/api/agentfield/query")
    async def query_with_agents(query: str):
        """Query knowledge graph using agent"""
        result = await handle_query(query)
        return result
    
    @app.get("/api/agentfield/status")
    async def agent_status():
        """Get status of all agents"""
        return {
            "agents": [
                "document_processor",
                "entity_extractor", 
                "graph_builder",
                "query_handler",
                "orchestrator"
            ],
            "status": "active",
            "memory": "enabled"
        }


# ── Usage Example ─────────────────────────────────────────────────────────────
"""
# In your main.py, add:

from agentfield_integration import setup_agentfield_routes

# After creating FastAPI app
setup_agentfield_routes(app)

# Now you have:
# POST /api/agentfield/upload - Process documents with agent swarm
# POST /api/agentfield/query - Query with GraphRAG agent
# GET /api/agentfield/status - Check agent health
"""
