# STREAMLIT CLOUD DEPLOYMENT GUIDE

This guide explains how to deploy to Streamlit Cloud (Option A) and **CRITICAL DATABASE LIMITATIONS**.

---

## ⚠️ **IMPORTANT: DATABASE LIMITATION**

### The Problem
Your app currently uses **SQLite** (`app.db`), which stores data locally on disk.

**Streamlit Cloud has an EPHEMERAL filesystem** - it deletes all local files when:
- The app restarts
- You push a new update
- The server restarts (can happen daily)

### What This Means
- ❌ **All user accounts will be deleted**
- ❌ **All usage tracking data will be lost**
- ❌ **App works for ~1 session, then resets**

### Example Timeline
```
Day 1: User creates account → Works ✅
Day 2: App restarts → User account GONE ❌
```

---

## 🔧 **SOLUTION: Use PostgreSQL Instead**

For production, you MUST use a hosted database (not SQLite).

### Recommended Free Options:

#### **Option 1: Render PostgreSQL (Easiest)**
1. Go to [render.com](https://render.com)
2. Create PostgreSQL database (free for 3 months)
3. Copy connection details
4. Add to Streamlit Cloud secrets (see below)

#### **Option 2: Supabase PostgreSQL**
1. Go to [supabase.com](https://supabase.com)
2. Create project (2 free projects, no sleep, no credit card)
3. Copy PostgreSQL connection string

---

## 📋 **STEP-BY-STEP DEPLOYMENT**

### Step 1: Revoke Exposed API Key
1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Delete the key: `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`
3. Create a NEW key and copy it

### Step 2: Update Local .streamlit/secrets.toml
```toml
GROQ_API_KEY = "your_new_groq_api_key_here"
```

### Step 3: Push to GitHub
```bash
git add .
git commit -m "Production-ready deployment"
git push origin main
```

### Step 4: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select:
   - GitHub repo: `your_username/your_repo`
   - Branch: `main`
   - Main file path: `app.py`
4. Click "Deploy"

### Step 5: Add Secrets (In Streamlit Cloud Dashboard)

1. Go to your app settings (⚙️ icon)
2. Click "Secrets"
3. Add your secrets in this format:
```
GROQ_API_KEY = "your_new_groq_api_key"
```

4. **Save** and app will restart with the secrets

---

## 🗄️ **DATABASE SETUP (For Persistent Data)**

### If Using SQLite (Current - NOT RECOMMENDED)
- Data will persist locally only
- Data WILL be lost on every deploy
- Only works for personal testing

### If Using PostgreSQL (RECOMMENDED)

#### Using Render:

1. Create database on [render.com](https://render.com)
2. Get connection details
3. Add to Streamlit Cloud secrets:
```
DB_HOST = "postgres://..."
DB_PORT = "5432"
DB_NAME = "your_db_name"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
```

4. Modify `app.py` to use PostgreSQL instead of SQLite:

Replace this:
```python
conn = sqlite3.connect("app.db")
```

With:
```python
import psycopg2
conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    port=st.secrets["DB_PORT"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"]
)
```

---

## 🚀 **QUICK DEPLOYMENT (SQLite - Testing Only)**

If you want to deploy NOW and deal with database later:

1. ✅ Revoke old API key
2. ✅ Update `.streamlit/secrets.toml` with new key
3. ✅ Push to GitHub
4. ✅ Deploy on Streamlit Cloud
5. ✅ Add secrets in Streamlit Cloud dashboard
6. ⚠️ **WARNING: Data will reset on app restart!**

---

## 🔍 **VERIFICATION CHECKLIST**

Before deploying, verify:

- [ ] Old API key revoked (console.groq.com/keys)
- [ ] New API key in `.streamlit/secrets.toml`
- [ ] `.env` NOT committed to git (check .gitignore)
- [ ] `.streamlit/secrets.toml` NOT committed to git
- [ ] `requirements.txt` has all dependencies
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud has API key in secrets dashboard

---

## 📊 **How Database Works (Current SQLite)**

### Local (Current Setup)
```
Your Computer
    ↓
SQLite Database (app.db)
    ↓
Persists on your disk
```

When you run `streamlit run app.py`:
1. App starts
2. `init_db()` checks if `app.db` exists
3. If not, creates tables (users, usage)
4. Users login/signup → Data stored in `app.db`
5. Data persists until you delete `app.db`

### Streamlit Cloud (Problem!)
```
Streamlit Server (Ephemeral Container)
    ↓
SQLite Database (app.db) - Temporary!
    ↓
Deleted on restart ❌
```

When deployed:
1. Container starts with clean filesystem
2. App creates fresh `app.db`
3. Users login/signup → Data stored in `app.db`
4. **Container restarts or app redeploys**
5. `app.db` DELETED → All data GONE ❌

### PostgreSQL (Solution!)
```
Streamlit Server (Ephemeral)
    ↓
PostgreSQL Server (Persistent, hosted elsewhere)
    ↓
Data persists forever ✅
```

When deployed:
1. Container starts (can be ephemeral)
2. App connects to remote PostgreSQL
3. Users login/signup → Data stored in PostgreSQL
4. **Container restarts or app redeploys**
5. PostgreSQL still has all data ✅
6. App reconnects to same database ✅

---

## ⚙️ **How Streamlit Secrets Work**

### Local (Development)
- `.streamlit/secrets.toml` stores your local secrets
- Not committed to git (in .gitignore)
- Accessed via: `st.secrets["YOUR_SECRET"]`

### Streamlit Cloud (Production)
- Secrets stored in Streamlit Cloud dashboard
- Never visible in code or git
- Accessed via: `st.secrets["YOUR_SECRET"]` (same code!)
- More secure - secrets not in git

---

## 🚨 **TROUBLESHOOTING**

### "API Key not configured" error
**Solution:** Add `GROQ_API_KEY` to Streamlit Cloud secrets dashboard

### "Database connection failed"
**Solution:** Check DB credentials in secrets. Verify database server is running.

### "Users disappeared after restart"
**Solution:** Normal if using SQLite. Migrate to PostgreSQL for persistence.

### "ModuleNotFoundError: psycopg2"
**Solution:** Add `psycopg2-binary` to `requirements.txt` if using PostgreSQL

---

## 📞 **Need Help?**

- Streamlit Cloud Docs: https://docs.streamlit.io/deploy/streamlit-cloud
- Render PostgreSQL: https://render.com/docs/databases
- Supabase PostgreSQL: https://supabase.com/docs/guides/getting-started
