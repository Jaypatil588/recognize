# 🚀 Complete Setup Guide - Recognize Project with Groq

## ✅ What's Already Done

1. ✅ Neo4j installed and running
2. ✅ Backend dependencies installed (Python venv)
3. ✅ Frontend dependencies installed (Node.js)
4. ✅ Groq API key configured
5. ✅ Main.py updated to use Groq instead of Claude
6. ✅ Backend server running on port 8000

## ⚠️ Current Issue: Neo4j Authentication

The Neo4j password in `.env` doesn't match the actual database password.

### Fix Neo4j Password (2 minutes):

**Option 1: Use Neo4j Browser (Easiest)**
1. Open http://localhost:7474 in your browser
2. Login with:
   - Username: `neo4j`
   - Password: Try `neo4j` (default) or `Durban@28`
3. If it asks to change password, set it to: `Durban@28`
4. Update `.env` file with the correct password

**Option 2: Reset Neo4j Password**
```bash
# Stop Neo4j
brew services stop neo4j

# Delete auth file
rm /opt/homebrew/var/neo4j/data/dbms/auth

# Start Neo4j
brew services start neo4j

# Connect with default password 'neo4j' and change it
cypher-shell -u neo4j -p neo4j
# Then run: ALTER USER neo4j SET PASSWORD 'Durban@28';
```

**Option 3: Update .env to match current password**
```bash
# Try connecting with different passwords
cypher-shell -u neo4j -p neo4j "RETURN 1;"
# If that works, update .env:
# NEO4J_PASSWORD="neo4j"
```

---

## 🎯 Quick Start (After fixing Neo4j)

### Terminal 1: Backend
```bash
cd /Users/tarang/CascadeProjects/windsurf-project/recognize/backend
source venv/bin/activate
python main.py
```

### Terminal 2: Frontend
```bash
cd /Users/tarang/CascadeProjects/windsurf-project/recognize
npm run dev
```

---

## 🔗 Access URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474

---

## 🧪 Test the System

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "groq": "connected",
  "neo4j": "running"
}
```

### 2. Test Groq Integration
```bash
cd backend
source venv/bin/activate
python groq_integration.py
```

Expected: `✅ Groq API working: Groq is working!`

### 3. Upload a Test Document
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@test.txt"
```

### 4. Query the Graph
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics?", "top_k": 5}'
```

---

## 📦 Dependencies Installed

### Backend (Python)
- ✅ fastapi
- ✅ uvicorn
- ✅ neo4j
- ✅ sentence-transformers
- ✅ groq (NEW - for Llama 3.3)
- ✅ pypdf
- ✅ python-docx
- ✅ networkx
- ✅ numpy

### Frontend (Node.js)
- ✅ react
- ✅ @react-three/fiber
- ✅ @react-three/drei
- ✅ three
- ✅ zustand
- ✅ d3-force

---

## 🔑 API Keys Configured

### Groq (Active)
```
GROQ_API_KEY=GROQ_API_KEY_REDACTED
```
- Model: `llama-3.3-70b-versatile`
- Speed: Ultra-fast inference
- Cost: Free tier available

---

## 🎨 What the System Does

1. **Upload Documents** (PDF, DOCX, TXT)
   - Extracts text
   - Chunks into manageable pieces
   - Processes with Groq AI

2. **Entity Extraction** (Groq Llama 3.3)
   - Identifies people, organizations, concepts, events
   - Extracts relationships between entities
   - Creates structured knowledge graph

3. **Graph Storage** (Neo4j)
   - Stores entities as nodes
   - Stores relationships as edges
   - Vector embeddings for semantic search

4. **3D Visualization** (React Three Fiber)
   - Interactive 3D graph
   - Rotate, zoom, explore
   - Click nodes for details

5. **GraphRAG Queries** (Groq + Neo4j)
   - Ask questions about your documents
   - Retrieves relevant context from graph
   - Generates answers with citations

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill if needed
kill -9 <PID>
```

### Frontend won't start?
```bash
# Check if port 5173 is in use
lsof -i :5173
# Kill if needed
kill -9 <PID>
```

### Neo4j connection errors?
```bash
# Check if Neo4j is running
brew services list | grep neo4j
# Restart if needed
brew services restart neo4j
```

### Groq API errors?
```bash
# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer GROQ_API_KEY_REDACTED"
```

---

## 📝 Files Modified

1. **backend/.env** - Added Groq API key
2. **backend/main.py** - Replaced Claude with Groq
3. **backend/groq_integration.py** - Groq helper functions
4. **backend/requirements.txt** - Added groq package
5. **backend/main_claude_backup.py** - Original Claude version (backup)

---

## 🎯 Next Steps for Hackathon

1. **Fix Neo4j password** (see above)
2. **Test end-to-end** (upload → extract → query)
3. **Integrate sponsor tools:**
   - AgentField (multi-agent orchestration)
   - TokenRouter (model routing)
   - Evermind (persistent memory)
   - Butterbase (backend services)
   - Zeabur (deployment)

4. **Polish demo:**
   - Create sample documents
   - Prepare talking points
   - Practice pitch

---

## 🏆 Hackathon Pitch

"We built a Context Graph system that turns documents into an interactive knowledge graph using Groq's ultra-fast Llama 3.3 model. Upload meeting notes, research papers, or any documents - our system extracts entities, builds relationships, and lets you query your knowledge with GraphRAG. It's like having a photographic memory for all your documents."

**Tech Stack:**
- Groq (Llama 3.3) - Entity extraction
- Neo4j - Graph database
- React Three Fiber - 3D visualization
- FastAPI - Backend API
- Sentence Transformers - Vector embeddings

---

## ✅ System Status

- ✅ Backend: Running on port 8000
- ✅ Frontend: Ready (npm run dev)
- ⚠️ Neo4j: Running but needs password fix
- ✅ Groq API: Connected and working

**Once Neo4j password is fixed, everything will be fully operational!**
