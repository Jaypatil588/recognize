# ⚡ Zeabur Deployment - Quick Start

## 🎯 What You Need (5 minutes setup)

### 1. Neo4j Aura (Free Cloud Database)
1. Go to https://neo4j.com/cloud/aura
2. Click **"Start Free"** → Create AuraDB Free instance
3. **SAVE THESE CREDENTIALS** (shown only once):
   ```
   URI: neo4j+s://xxxxx.databases.neo4j.io
   Username: neo4j
   Password: [auto-generated]
   ```

### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Deploy to Zeabur"
git remote add origin https://github.com/YOUR_USERNAME/Recognize.git
git push -u origin main
```

---

## 🚀 Deploy in 3 Steps

### Step 1: Deploy Backend

1. Go to [zeabur.com/dashboard](https://zeabur.com/dashboard)
2. **Create Project** → Name: `recognize`
3. **Add Service** → **Git** → Select your repo
4. **Settings**:
   - Root Directory: `backend`
   - Port: `8000`
5. **Variables** (click Variables tab):
   ```env
   GROQ_API_KEY=GROQ_API_KEY_REDACTED
   NEO4J_URI=neo4j+s://YOUR_AURA_URI_HERE
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=YOUR_AURA_PASSWORD_HERE
   ```
6. **Deploy** → Wait 2-3 mins
7. **Copy backend URL**: `https://recognize-backend-xxx.zeabur.app`

### Step 2: Deploy Frontend

1. In same project, **Add Service** → **Git** → Same repo
2. **Variables**:
   ```env
   VITE_API_URL=https://recognize-backend-xxx.zeabur.app
   ```
   (Use your actual backend URL from Step 1)
3. **Deploy** → Wait 2-3 mins
4. **Get frontend URL**: `https://recognize-xxx.zeabur.app`

### Step 3: Update CORS

1. Update `backend/main.py` line 36:
   ```python
   allow_origins=[
       "*",  # For hackathon demo - restrict in production
   ],
   ```
2. Commit and push:
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push
   ```
3. Zeabur auto-redeploys backend

---

## ✅ Test Your Deployment

1. Visit your frontend URL
2. Upload `demo_meeting_5min.txt`
3. See the 3D graph visualization
4. Query: "What is Tarang working on?"

---

## 🐛 Troubleshooting

**Backend won't start?**
- Check Zeabur logs: Service → Logs tab
- Verify Neo4j Aura credentials
- Ensure `NEO4J_URI` starts with `neo4j+s://`

**Frontend can't connect?**
- Verify `VITE_API_URL` is set correctly
- Check backend is running (visit `/health` endpoint)
- Backend URL should NOT have trailing slash

**Neo4j timeout?**
- Neo4j Aura free tier pauses after 3 days inactivity
- Wake it up by visiting Aura console

---

## 💰 Cost

**Everything is FREE:**
- ✅ Zeabur: 2 services on free tier
- ✅ Neo4j Aura: 200k nodes free
- ✅ Groq: 14,400 requests/day free

---

## 📝 Files Created for Deployment

- ✅ `backend/Dockerfile` - Backend container config
- ✅ `backend/.dockerignore` - Exclude unnecessary files
- ✅ `zbpack.json` - Zeabur frontend config
- ✅ `src/api.js` - Updated with env variable support
- ✅ `DEPLOYMENT.md` - Full deployment guide

---

## 🎉 You're Done!

Your Recognize app is now live on Zeabur! Share the frontend URL with judges and users.

**Demo URL**: `https://recognize-xxx.zeabur.app`

For detailed troubleshooting, see `DEPLOYMENT.md`.
