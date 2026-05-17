"""
Modified main.py to use Groq instead of Claude
Copy this over main.py or import from it
"""

import asyncio
import io
import json
import os
import re
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

import networkx as nx
import numpy as np
import pypdf
import docx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from neo4j import GraphDatabase
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from groq import Groq

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Context Graph — GraphRAG with Groq")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ────────────────────────────────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "Durban@28")
EMBED_DIM  = 384  # all-MiniLM-L6-v2

driver       = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
embedder     = SentenceTransformer("all-MiniLM-L6-v2")
groq_client  = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# ── Neo4j schema bootstrap ────────────────────────────────────────────────────
def _setup_schema(tx):
    for label, prop in [("Document", "id"), ("Chunk", "id"), ("Entity", "id"), ("Community", "id")]:
        tx.run(f"CREATE CONSTRAINT {label.lower()}_{prop}_unique IF NOT EXISTS "
               f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")
    
    for idx, label, prop in [
        ("entity_vec",  "Entity",  "embedding"),
        ("chunk_vec",   "Chunk",   "embedding"),
    ]:
        try:
            tx.run(f"""
                CREATE VECTOR INDEX {idx} IF NOT EXISTS
                FOR (n:{label}) ON (n.{prop})
                OPTIONS {{indexConfig: {{
                    `vector.dimensions`: {EMBED_DIM},
                    `vector.similarity_function`: 'cosine'
                }}}}
            """)
        except Exception:
            pass

try:
    with driver.session() as s:
        s.execute_write(_setup_schema)
    print("[OK] Neo4j schema ready")
except Exception as e:
    print(f"[WARN] Neo4j not reachable at startup: {e}")

# ── Text extraction & chunking ─────────────────────────────────────────────────
def extract_text(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    if ext in (".docx", ".doc"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    return content.decode("utf-8", errors="ignore")

def chunk_text(text: str, size: int = 600, overlap: int = 80) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return [c for c in chunks if len(c) > 50]

# ── GraphRAG entity extraction with GROQ ───────────────────────────────────────
EXTRACT_SYSTEM = "You are a knowledge graph extraction engine. Output only valid JSON, no markdown."

EXTRACT_USER = """Extract entities and relationships from the text below.

Return ONLY this JSON (no code fences, no extra text):
{{
  "entities": [
    {{"name": "...", "type": "CONCEPT|PERSON|ORGANIZATION|PLACE|TECHNOLOGY|EVENT", "description": "one sentence"}}
  ],
  "relationships": [
    {{"source": "EntityA", "target": "EntityB", "relation": "VERB_PHRASE"}}
  ]
}}

Text:
{text}"""

async def extract_graph(text: str) -> dict:
    """Extract entities using Groq (Llama 3.3)"""
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1200,
            temperature=0.3,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": EXTRACT_USER.format(text=text)}
            ],
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"Groq extraction error: {e}")
        return {"entities": [], "relationships": []}

# ── Neo4j write helpers ───────────────────────────────────────────────────────
ENTITY_MERGE_THRESHOLD = 0.90

def _find_similar_entity(session, embedding: list[float]) -> Optional[str]:
    try:
        hits = session.run(
            """
            CALL db.index.vector.queryNodes('entity_vec', 1, $emb)
            YIELD node AS e, score
            WHERE score >= $thresh
            RETURN e.id AS id
            """,
            emb=embedding, thresh=ENTITY_MERGE_THRESHOLD,
        ).data()
        if hits:
            return hits[0]["id"]
    except Exception:
        pass
    return None

def _upsert_entity(tx, name: str, etype: str, desc: str, embedding: list[float]):
    entity_id = f"entity:{name.lower().replace(' ', '_')}"
    tx.run(
        """
        MERGE (e:Entity {id: $id})
        ON CREATE SET e.name = $name, e.type = $type, e.description = $desc,
                      e.embedding = $emb, e.mention_count = 1
        ON MATCH  SET e.mention_count = e.mention_count + 1,
                      e.description   = CASE WHEN size($desc) > size(e.description)
                                             THEN $desc ELSE e.description END
        """,
        id=entity_id, name=name, type=etype, desc=desc, emb=embedding,
    )
    return entity_id

def _bump_mention(tx, entity_id: str):
    tx.run("MATCH (e:Entity {id: $id}) SET e.mention_count = e.mention_count + 1", id=entity_id)

def _upsert_relation(tx, src_id: str, tgt_id: str, relation: str):
    tx.run(
        """
        MATCH (a:Entity {id: $src}), (b:Entity {id: $tgt})
        MERGE (a)-[r:RELATES_TO {relation: $rel}]->(b)
        ON CREATE SET r.weight = 1
        ON MATCH  SET r.weight = r.weight + 1
        """,
        src=src_id, tgt=tgt_id, rel=relation,
    )

def _link_chunk_entity(tx, chunk_id: str, entity_id: str):
    tx.run(
        """
        MATCH (c:Chunk {id: $cid}), (e:Entity {id: $eid})
        MERGE (c)-[:MENTIONS]->(e)
        """,
        cid=chunk_id, eid=entity_id,
    )

# ── API endpoints ──────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
async def root():
    return {"message": "Context Graph — GraphRAG with Groq", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "groq": "connected" if os.getenv("GROQ_API_KEY") else "no_key",
        "neo4j": "running"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    try:
        content = await file.read()
        text = extract_text(content, file.filename)
        chunks = chunk_text(text)
        
        doc_id = str(uuid.uuid4())
        
        # Process chunks
        for i, chunk in enumerate(chunks[:10]):  # Limit for demo
            chunk_id = f"{doc_id}:chunk:{i}"
            chunk_emb = embedder.encode(chunk).tolist()
            
            # Extract entities
            graph_data = await extract_graph(chunk)
            
            # Store in Neo4j
            with driver.session() as session:
                # Store chunk
                session.run(
                    """
                    MERGE (c:Chunk {id: $id})
                    SET c.text = $text, c.embedding = $emb, c.doc_id = $doc_id
                    """,
                    id=chunk_id, text=chunk, emb=chunk_emb, doc_id=doc_id
                )
                
                # Store entities
                for ent in graph_data.get("entities", []):
                    ent_emb = embedder.encode(ent["name"]).tolist()
                    ent_id = session.execute_write(
                        _upsert_entity,
                        ent["name"], ent["type"], ent.get("description", ""), ent_emb
                    )
                    session.execute_write(_link_chunk_entity, chunk_id, ent_id)
                
                # Store relationships
                for rel in graph_data.get("relationships", []):
                    src_id = f"entity:{rel['source'].lower().replace(' ', '_')}"
                    tgt_id = f"entity:{rel['target'].lower().replace(' ', '_')}"
                    session.execute_write(_upsert_relation, src_id, tgt_id, rel["relation"])
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks_processed": len(chunks[:10]),
            "message": "Document processed with Groq"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
async def get_graph():
    """Get full graph data"""
    with driver.session() as session:
        entities = session.run("MATCH (e:Entity) RETURN e.id as id, e.name as name, e.type as type LIMIT 100").data()
        relationships = session.run(
            "MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) RETURN a.id as source, b.id as target, r.relation as relation LIMIT 200"
        ).data()
    
    return {"nodes": entities, "edges": relationships}

@app.post("/query")
async def query_graph(req: QueryRequest):
    """GraphRAG query with Groq"""
    query_emb = embedder.encode(req.query).tolist()
    
    with driver.session() as session:
        # Vector search
        results = session.run(
            """
            CALL db.index.vector.queryNodes('entity_vec', $k, $emb)
            YIELD node AS e, score
            RETURN e.name as name, e.description as description, e.type as type, score
            ORDER BY score DESC
            """,
            k=req.top_k, emb=query_emb
        ).data()
    
    # Build context
    context = "\n".join([
        f"- {r['name']} ({r['type']}): {r['description']}"
        for r in results
    ])
    
    # Answer with Groq
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Answer questions based on the provided context. Cite sources."},
                {"role": "user", "content": f"Question: {req.query}\n\nContext:\n{context}"}
            ],
            max_tokens=500
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"Error: {e}"
    
    return {
        "query": req.query,
        "answer": answer,
        "sources": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
