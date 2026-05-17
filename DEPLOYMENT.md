# 🚀 Deploying Recognize to Zeabur

This guide will help you deploy the Recognize application to Zeabur.

## Prerequisites

1. **Zeabur Account**: Sign up at [zeabur.com](https://zeabur.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Neo4j Aura Account**: Free cloud Neo4j database at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura)
4. **Groq API Key**: Get from [console.groq.com](https://console.groq.com)

---

## Step 1: Set Up Neo4j Aura (Cloud Database)

Since Zeabur doesn't provide Neo4j hosting, we'll use Neo4j Aura Free:

1. Go to https://neo4j.com/cloud/aura
2. Click **"Start Free"**
3. Create a new **AuraDB Free** instance
4. **IMPORTANT**: Save the credentials shown (you won't see them again!)
   - Connection URI (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username (usually `neo4j`)
   - Password (auto-generated)

5. Wait for instance to be ready (2-3 minutes)

---

## Step 2: Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for Zeabur deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/Recognize.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy Backend to Zeabur

### 3.1 Create New Project

1. Go to [zeabur.com/dashboard](https://zeabur.com/dashboard)
2. Click **"Create Project"**
3. Name it `recognize-backend`

### 3.2 Add Backend Service

1. Click **"Add Service"**
2. Select **"Git"**
3. Connect your GitHub account
4. Select your `Recognize` repository
5. Zeabur will auto-detect the Dockerfile in `/backend`

### 3.3 Configure Environment Variables

Click on the service → **"Variables"** tab → Add these:

```env
GROQ_API_KEY=GROQ_API_KEY_REDACTED
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password_here
```

### 3.4 Set Root Directory

1. Go to **"Settings"** tab
2. Set **Root Directory**: `backend`
3. Set **Port**: `8000`

### 3.5 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Once deployed, you'll get a URL like: `https://recognize-backend-xxx.zeabur.app`

---

## Step 4: Deploy Frontend to Zeabur

### 4.1 Add Frontend Service

1. In the same project, click **"Add Service"** again
2. Select **"Git"** → Same repository
3. Zeabur will detect it's a Vite app

### 4.2 Configure Environment Variables

Add this variable:

```env
VITE_API_URL=https://recognize-backend-xxx.zeabur.app
```

Replace with your actual backend URL from Step 3.

### 4.3 Update Frontend API Configuration

Before deploying, update the frontend to use the environment variable:

**Edit `src/api.js`:**

```javascript
const BASE = import.meta.env.VITE_API_URL || '/api'
```

Commit and push this change:

```bash
git add src/api.js
git commit -m "Use environment variable for API URL"
git push
```

### 4.4 Set Root Directory

1. Go to **"Settings"** tab
2. Keep **Root Directory** as `.` (root)
3. Set **Port**: `5173` (or use default)

### 4.5 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. You'll get a URL like: `https://recognize-xxx.zeabur.app`

---

## Step 5: Enable CORS on Backend

Update `backend/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://recognize-xxx.zeabur.app",  # Add your Zeabur frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:

```bash
git add backend/main.py
git commit -m "Add Zeabur frontend to CORS"
git push
```

Zeabur will auto-redeploy the backend.

---

## Step 6: Test Your Deployment

1. Visit your frontend URL: `https://recognize-xxx.zeabur.app`
2. Upload a test document
3. Verify the graph visualization appears
4. Try querying the graph

---

## Troubleshooting

### Backend Won't Start

**Check logs in Zeabur dashboard:**
- Go to service → **"Logs"** tab
- Look for errors related to:
  - Missing environment variables
  - Neo4j connection issues
  - Python dependency errors

**Common fixes:**
- Verify Neo4j Aura credentials are correct
- Ensure `NEO4J_URI` uses `neo4j+s://` (secure connection)
- Check Groq API key is valid

### Frontend Can't Connect to Backend

**Check:**
1. Backend is deployed and running (green status in Zeabur)
2. `VITE_API_URL` environment variable is set correctly
3. CORS is configured with frontend URL
4. Backend URL is accessible (visit `/health` endpoint)

### Neo4j Connection Timeout

**Solutions:**
- Neo4j Aura free tier may pause after inactivity - wake it up by visiting the Aura console
- Check firewall rules in Neo4j Aura (should allow all IPs by default)
- Verify connection string format: `neo4j+s://xxxxx.databases.neo4j.io`

---

## Production Optimizations

### 1. Custom Domain

In Zeabur:
1. Go to service → **"Domains"**
2. Click **"Add Domain"**
3. Add your custom domain (e.g., `recognize.yourdomain.com`)
4. Update DNS records as instructed

### 2. Environment-Specific Configs

Create separate Zeabur projects for:
- **Development**: `recognize-dev`
- **Production**: `recognize-prod`

### 3. Monitoring

Enable Zeabur monitoring:
- Go to **"Metrics"** tab
- Monitor CPU, memory, and request rates
- Set up alerts for downtime

### 4. Auto-Scaling

Zeabur automatically scales based on traffic, but you can configure:
- Min/max instances
- CPU/memory limits
- Auto-sleep for inactivity

---

## Cost Estimate

**Zeabur Free Tier:**
- ✅ 2 services (backend + frontend)
- ✅ 512MB RAM per service
- ✅ Auto-sleep after 7 days inactivity
- ✅ Custom domains

**Neo4j Aura Free:**
- ✅ 200k nodes + relationships
- ✅ 50MB storage
- ✅ Pauses after 3 days inactivity

**Groq:**
- ✅ Free tier: 14,400 requests/day
- ✅ No credit card required

**Total Monthly Cost: $0** 🎉

---

## Support

- **Zeabur Docs**: https://zeabur.com/docs
- **Neo4j Aura Docs**: https://neo4j.com/docs/aura
- **Groq Docs**: https://console.groq.com/docs

---

## Quick Deploy Checklist

- [ ] Neo4j Aura instance created and credentials saved
- [ ] Code pushed to GitHub
- [ ] Backend service created in Zeabur
- [ ] Backend environment variables configured
- [ ] Backend deployed successfully
- [ ] Frontend service created in Zeabur
- [ ] Frontend environment variable set
- [ ] Frontend API URL updated
- [ ] CORS configured with frontend URL
- [ ] Both services deployed and accessible
- [ ] Test upload and query functionality

**Your Recognize app is now live! 🚀**
