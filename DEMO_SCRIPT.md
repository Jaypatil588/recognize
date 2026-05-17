# 🎬 Recognize - 4-Minute Demo Script

**Team**: Vedant (Lead), Tarang (Backend), Rishi (Data), Jay (Frontend)

---

## 📋 DEMO FLOW (4 minutes)

### [0:00 - 0:30] Introduction - Vedant

**Vedant**: "Hi everyone! We're Team Recognize, and we're solving a massive problem - **80% of meeting knowledge is lost within 48 hours**. Companies conduct millions of meetings, but all that valuable information just disappears into scattered notes and forgotten recordings."

"We built **Recognize** - an AI-powered meeting intelligence platform that transforms unstructured meeting transcripts into an interactive, searchable knowledge graph."

---

### [0:30 - 1:15] Tech Stack Overview - Tarang

**Tarang**: "Let me walk you through our tech stack. We're using **Groq's Llama 3.3 70B model** for ultra-fast entity extraction - we're talking 300+ tokens per second. This gives us real-time processing of meeting transcripts with 92-95% accuracy."

"The backend is built with **FastAPI** in Python, and we're using **Neo4j** as our graph database to store entities and relationships. We've also integrated **AgentField** for multi-agent orchestration and **TokenRouter** for smart model routing with caching."

"For embeddings, we're using Sentence Transformers to enable semantic search across all meetings."

---

### [1:15 - 2:15] Live Demo - Rishi

**Rishi**: "Let me show you how it works. Here's a real meeting transcript from our team - a 5-minute discussion about our platform architecture."

*[Opens localhost:5173 or deployed URL]*

"Watch as I upload this transcript..."

*[Uploads demo_meeting_5min.txt]*

"In just a few seconds, Groq has extracted **17 entities** - including people like Vedant, Tarang, Jay, and me, plus concepts like 'Audio File Processing', 'Transcription', 'Organization Structure', and 'Brain Animation'."

"The system also identified **45 relationships** between these entities. For example, it knows that Tarang is working on audio file processing, I'm handling the organizational structure visualization, and Jay is designing the API integration."

*[Shows 3D graph visualization]*

"This is our 3D brain-inspired visualization built with React Three Fiber. Each node represents an entity, and the connections show semantic relationships."

---

### [2:15 - 3:00] Query Demo - Jay

**Jay**: "The real power is in querying. Let me ask the system: **'What is Tarang working on?'**"

*[Types query in chat panel]*

"The system uses GraphRAG - that's Graph Retrieval-Augmented Generation. It does a vector similarity search across all entities, finds the most relevant context, and uses Groq to generate a natural language answer."

*[Shows answer]*

"It tells us Tarang is working on audio file processing and transcription, with specific citations from the meeting. This works across **all meetings** - imagine querying your entire company's meeting history with natural language."

---

### [3:00 - 3:45] Market & Impact - Vedant

**Vedant**: "The market opportunity is huge. We're targeting the **$8 billion meeting intelligence market** - enterprise teams, consulting firms, remote-first companies, and educational institutions."

"Our key differentiators:"
- "**Graph-based knowledge** - not just transcripts, but semantic relationships"
- "**Cross-meeting search** - find decisions made months ago instantly"
- "**Visual intelligence** - see how knowledge connects across your organization"
- "**Real-time processing** - Groq's LPU makes it instant"

"We're using **6 sponsor tools** - Groq, Neo4j, Zeabur, AgentField, TokenRouter, and Evermind - to build a production-ready platform."

---

### [3:45 - 4:00] Closing - Tarang

**Tarang**: "We've deployed this to **Zeabur** for one-click scaling. The entire stack is containerized, and we're using Neo4j Aura for cloud database hosting."

**Vedant**: "Companies lose millions in productivity because meeting knowledge disappears. **Recognize preserves institutional memory** and makes it searchable. Thank you!"

---

## 🎯 KEY TALKING POINTS

### Problem
- 80% of meeting knowledge lost in 48 hours
- Scattered notes, inaccessible recordings
- New team members can't access historical context

### Solution
- AI-powered entity extraction (Groq)
- Knowledge graph (Neo4j)
- 3D visualization (React Three Fiber)
- Natural language queries (GraphRAG)

### Tech Stack
- **AI**: Groq (Llama 3.3 70B), Sentence Transformers
- **Backend**: FastAPI, Python 3.13
- **Database**: Neo4j (graph + vector search)
- **Frontend**: React, React Three Fiber, Vite
- **Deployment**: Zeabur, Docker
- **Sponsors**: Groq, Neo4j, Zeabur, AgentField, TokenRouter, Evermind

### Market
- TAM: $50B (collaboration software)
- SAM: $8B (meeting intelligence)
- Target: Enterprise teams, consulting firms, remote companies

### Demo Stats
- 17 entities extracted
- 45 relationships mapped
- 92-95% extraction accuracy
- Sub-second query response

---

## 📱 BACKUP TALKING POINTS

**If demo fails:**
"We have a fully working local version. For demo stability, let me show you the architecture and code..."

**If time runs short:**
Skip the query demo, focus on visualization and tech stack.

**If judges ask about scalability:**
"Neo4j handles millions of nodes, Groq processes 300+ tokens/sec, Zeabur auto-scales. We're production-ready."

**If judges ask about accuracy:**
"92-95% entity extraction accuracy with Groq. We use vector embeddings for semantic search with 88%+ precision."

---

## 🎬 PRESENTATION TIPS

1. **Vedant**: Confident, problem-focused, market-aware
2. **Tarang**: Technical, precise, knows the stack deeply
3. **Rishi**: Demo-focused, shows the product working
4. **Jay**: Query-focused, explains GraphRAG clearly

**Energy**: High, enthusiastic, but professional
**Pace**: Fast but clear - you have 4 minutes!
**Visuals**: Keep the demo visible at all times

---

## ✅ PRE-DEMO CHECKLIST

- [ ] Backend running (localhost:8000 or Zeabur)
- [ ] Frontend running (localhost:5173 or Zeabur)
- [ ] Neo4j connected and populated
- [ ] Demo file ready (demo_meeting_5min.txt)
- [ ] Graph showing 17 nodes, 45 relationships
- [ ] Test query works: "What is Tarang working on?"
- [ ] Browser tabs open and ready
- [ ] Team knows their parts
- [ ] Backup plan if demo fails

---

**GOOD LUCK! 🚀**
