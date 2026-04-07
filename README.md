# AI Content Pro+ 🚀

An AI-powered content generation platform using Streamlit and Groq API. Generate Instagram, YouTube, and content ideas with AI assistance.

## ⚠️ **IMPORTANT FOR STREAMLIT CLOUD DEPLOYMENT**

**Before deploying, read [`STREAMLIT_CLOUD_GUIDE.md`](STREAMLIT_CLOUD_GUIDE.md)**

Critical issues:
- SQLite data will be deleted on app restart (use PostgreSQL for production)
- Secrets must be added to Streamlit Cloud dashboard
- Old API key must be revoked

## Features

- 🔐 **User Authentication** - Secure signup and login
- 📊 **Usage Tracking** - Monitor API usage with limits
- 📝 **Content Generation** - Instagram, YouTube, and Ideas
- 📄 **RAG Support** - Upload PDFs for context-aware generation
- 🎨 **Clean UI** - Streamlit-based responsive interface

## Prerequisites

- Python 3.11+
- Groq API Key ([Get it here](https://console.groq.com/keys))
- Virtual environment (recommended)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd Project
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 5. Run the application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

---

## Deployment

### Option 1: Docker (Recommended)

```bash
docker build -t ai-content-pro .
docker run -p 8501:8501 --env-file .env ai-content-pro
```

### Option 2: Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add `GROQ_API_KEY` as a secret in Streamlit Cloud dashboard

### Option 3: Heroku / Railway / Render

See deployment guides below for each platform.

---

## Database Solutions (Free Tier)

Currently, the app uses **SQLite** for local development. For production with multiple users, you need a hosted database.

### **RECOMMENDED: Render PostgreSQL (Best Free Option)**

1. Go to [render.com](https://render.com)
2. Create account (free tier available)
3. Create a PostgreSQL database
4. Get connection details (note: Render free tier sleeps after 15 min inactivity)
5. Update `.env`:
```env
DB_HOST=<your-render-host>
DB_PORT=5432
DB_NAME=<your-db-name>
DB_USER=<your-user>
DB_PASSWORD=<your-password>
```

**Pros:** Free tier, simple setup, good performance
**Cons:** Sleeps after 15 minutes of inactivity

### **Alternative: Supabase PostgreSQL (Free + Realtime)**

1. Go to [supabase.com](https://supabase.com)
2. Create project (free tier: 2 projects, 500MB storage)
3. Get PostgreSQL connection string
4. Update code to use:
```python
# Replace sqlite with psycopg2
# pip install psycopg2-binary
```

**Pros:** Free tier generous, built-in authentication, real-time features
**Cons:** Limited to 2 free projects

### **Alternative: MongoDB Atlas (Free Tier)**

1. Go to [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create cluster (free tier: 512MB storage)
3. Get connection string
4. Update code to use PyMongo

**Pros:** NoSQL flexibility, 512MB free storage
**Cons:** Requires code changes to use MongoDB

### **Budget Alternative: PlanetScale MySQL (Free)**

1. Go to [planetscale.com](https://planetscale.com)
2. Create account (free tier: 1 database, 5GB storage)
3. Get connection string

**Pros:** Free MySQL database, good for testing, up to 5GB
**Cons:** Limited to 1 free database

---

## Quick Setup for Production

### Using Render (Recommended):

1. **Database Setup:**
   - Create Render PostgreSQL database
   - Get connection string

2. **Deploy App:**
   ```bash
   # Push to GitHub
   git push origin main
   
   # On Render dashboard:
   # - New Web Service
   # - Connect GitHub repo
   # - Set environment: `python`
   # - Build command: `pip install -r requirements.txt`
   # - Start command: `streamlit run app.py --server.port=10000`
   # - Add .env secrets: GROQ_API_KEY, DB_* variables
   ```

3. **First Run:**
   - Database tables auto-create on first run
   - Visit your app URL

---

## Environment Variables

```env
# Required
GROQ_API_KEY=your_api_key_here

# Database (optional - defaults to SQLite)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
```

---

## Security Checklist

- ✅ Never commit `.env` file
- ✅ Regenerate API keys if exposed
- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS on production
- ✅ Set strong database passwords
- ✅ Keep dependencies updated

---

## Troubleshooting

### Issue: "GROQ_API_KEY not configured"
**Solution:** Check your `.env` file and ensure `GROQ_API_KEY` is set correctly.

### Issue: Out of memory with large PDFs
**Solution:** Increase file size limit in `app.py` or use cloud storage.

### Issue: Database connection error
**Solution:** Check database credentials and network connectivity.

### Issue: Slow performance on Render free tier
**Solution:** Database sleeps after 15 min. Consider paid tier or alternative.

---

## Monitoring & Logs

For production deployments, configure logging:

```python
# Logs are in the app.py logger
# Check deployment logs in Render/Heroku dashboard
```

---

## Cost Estimation (Monthly)

| Component | Cost | Notes |
|-----------|------|-------|
| Groq API | Variable | ~$0.10-1 per 1M tokens |
| Database | Free-$15 | Free tier available on Render/Supabase |
| Hosting | Free-$5 | Streamlit Cloud free, Render $5+ |
| **Total** | **Free-$20** | Depends on usage |

---

## Support

- 📖 [Streamlit Docs](https://docs.streamlit.io)
- 🔑 [Groq API Docs](https://console.groq.com/docs)
- 🐳 [Docker Docs](https://docs.docker.com)

---

## License

See [LICENSE](LICENSE) file.
