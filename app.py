import os
import uuid
import sqlite3
import streamlit as st
import logging
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from streamlit_option_menu import option_menu
from passlib.context import CryptContext

# LangChain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------- ENV (Works on local and Streamlit Cloud) ----------------
# On local: uses .streamlit/secrets.toml
# On Streamlit Cloud: uses secrets dashboard
load_dotenv()

@st.cache_resource
def get_groq_client():
    """Initialize Groq client with API key from secrets"""
    try:
        # Try Streamlit secrets first (Streamlit Cloud), then environment
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        else:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            logger.error("GROQ_API_KEY not configured")
            st.error("❌ API Key not configured. Please add GROQ_API_KEY to .streamlit/secrets.toml (local) or Streamlit Cloud dashboard.")
            st.stop()
        
        client = Groq(api_key=api_key)
        logger.info("Groq client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        st.error("❌ Failed to initialize AI client. Please check your API key.")
        st.stop()

client = get_groq_client()

st.set_page_config(page_title="AI Content Pro+", layout="wide")

# ---------------- TEMP FILE CLEANUP ----------------
def cleanup_temp_files():
    """Clean up temporary PDF files"""
    try:
        temp_files = Path(".").glob("temp_*.pdf")
        for file in temp_files:
            if file.exists():
                file.unlink()
                logger.info(f"Cleaned up {file}")
    except Exception as e:
        logger.warning(f"Error cleaning temp files: {e}")

# Run cleanup on app start
cleanup_temp_files()

# ---------------- PASSWORD ----------------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            username TEXT,
            count INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ----------------
def create_user(username, email, password):
    """Create a new user account"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    try:
        hashed_pw = pwd_context.hash(password)

        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        logger.info(f"User created: {username}")
        return True, "Account created successfully"

    except sqlite3.IntegrityError:
        logger.warning(f"Signup failed: Username already exists - {username}")
        return False, "Username already exists"
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return False, "An error occurred during signup"
    finally:
        conn.close()


def login_user(username, email, password):
    """Authenticate user"""
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    try:
        c.execute("SELECT username, email, password FROM users WHERE username=? or email=?", (username, email))
        data = c.fetchone()
        
        if data:
            st.session_state.user = data[0]
            st.session_state.email = data[1]
            is_valid = pwd_context.verify(password, data[2])
            if is_valid:
                logger.info(f"User logged in: {data[0]}")
            return is_valid
        
        logger.warning(f"Login attempt failed for: {username or email}")
        return False
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False
    finally:
        conn.close()

# ---------------- USAGE ----------------
def get_usage(username):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    c.execute("SELECT count FROM usage WHERE username=?", (username,))
    data = c.fetchone()

    conn.close()
    return data[0] if data else 0


def increment_usage(username):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    c.execute("SELECT count FROM usage WHERE username=?", (username,))
    data = c.fetchone()

    if data:
        c.execute("UPDATE usage SET count = count + 1 WHERE username=?", (username,))
    else:
        c.execute("INSERT INTO usage (username, count) VALUES (?, 1)", (username,))

    conn.commit()
    conn.close()

LIMIT = 10

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 AI Content Pro+")

    choice = option_menu(
        menu_title=None,
        options=["Login", "Signup"],
        icons=["house", "create"],
        orientation="horizontal",
        styles={
            "container": {"padding": "5px", "background-color": "#f5b1b4","border": "1px solid black"},
            "icon": {"color": "#0e0e0e", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "color": "#111111",
                "text-align": "center",
                "margin": "3px",
            },
            "nav-link-selected": {
                "background-color": "#e35252",
                "color": "white",
                "font-weight": "bold",
            },
            
        },
    )

    username = st.text_input("Username")
    email = st.text_input("Email (optional)")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account", use_container_width=True):
            success, message = create_user(username, email, password)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

    else:
        if st.button("Login", use_container_width=True):
            if login_user(username, email, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- TOP NAVIGATION ----------------
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Instagram", "YouTube", "Ideas", "Profile"],
    icons=["house", "instagram", "youtube", "lightbulb", "person"],
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#bd834a"},
        "icon": {"color": "#ebf1f3", "font-size": "18px"},
        "nav-link": {
            "font-size": "14px",
            "color": "#ebf1f3",
            "text-align": "center",
            "margin": "3px",
            "border-radius": "8px",
        },
        "nav-link-selected": {
            "background-color": "#402b02",
            "color": "white",
            "font-weight": "bold",
        },
    },
)

page = selected


# ---------------- RAG ----------------
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

def process_file(uploaded_file):
    """Process uploaded PDF file for RAG"""
    if not uploaded_file:
        return None
    
    try:
        # Validate file size
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error(f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB")
            return None
        
        file_path = f"temp_{uuid.uuid4()}.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        if not docs:
            st.warning("No content found in PDF")
            return None

        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings()
        db = FAISS.from_documents(chunks, embeddings)

        logger.info(f"PDF processed successfully: {uploaded_file.name}")
        return db
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        st.error(f"Error processing PDF: {str(e)[:100]}")
        return None


def get_context(db, query):
    """Retrieve relevant context from vector store"""
    if db:
        try:
            results = db.similarity_search(query, k=2)
            return "\n".join([r.page_content for r in results])
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    return ""

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📊 Dashboard")

    usage = get_usage(st.session_state.user)
    remaining = LIMIT - usage

    # Create outer columns for centering
    left, center, right = st.columns([1, 2, 1])

    with center:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Usage", usage)

        with col2:
            st.metric("Limit", LIMIT)

        with col3:
            st.metric("Remaining", remaining)

        st.info("🚀 Your AI Content Engine is ready!")

# ---------------- INSTAGRAM ----------------
elif page == "Instagram":
    st.title("📸 Instagram Generator")

    topic = st.text_input("Enter topic", placeholder="Enter your content idea...")
    uploaded_file = st.file_uploader("Upload PDF (optional)", type="pdf")

    if st.button("Generate", use_container_width=True):
        if not topic or len(topic.strip()) < 2:
            st.error("Please enter a topic")
            st.stop()
        
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True):
                st.session_state.show_upgrade = True
            st.stop()

        try:
            with st.spinner("Generating content..."):
                db = process_file(uploaded_file)
                context = get_context(db, topic)

                output = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{context}\nInstagram content for {topic}"}]
                )

                increment_usage(st.session_state.user)
                st.write(output.choices[0].message.content)
                logger.info(f"Instagram content generated for: {topic}")
        except Exception as e:
            logger.error(f"Error generating Instagram content: {e}")
            st.error(f"Error generating content: {str(e)[:100]}")

# ---------------- YOUTUBE ----------------
elif page == "YouTube":
    st.title("🎬 YouTube Generator")

    topic = st.text_input("Enter topic", placeholder="Enter video idea...")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if st.button("Generate", use_container_width=True):
        if not topic or len(topic.strip()) < 2:
            st.error("Please enter a topic")
            st.stop()
        
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True,disabled=True):
                st.session_state.show_upgrade = True
            st.stop()

        try:
            with st.spinner("Generating script..."):
                db = process_file(uploaded_file)
                context = get_context(db, topic)

                output = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{context}\nYouTube script for {topic}"}]
                )

                increment_usage(st.session_state.user)
                st.write(output.choices[0].message.content)
                logger.info(f"YouTube script generated for: {topic}")
        except Exception as e:
            logger.error(f"Error generating YouTube script: {e}")
            st.error(f"Error generating script: {str(e)[:100]}")

# ---------------- IDEAS ----------------
elif page == "Ideas":
    st.title("💡 Ideas Generator")

    topic = st.text_input("Enter topic", placeholder="Enter niche or topic...")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if st.button("Generate Ideas", use_container_width=True):
        if not topic or len(topic.strip()) < 2:
            st.error("Please enter a topic")
            st.stop()
        
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True):
                st.session_state.show_upgrade = True

            st.stop()
        
        try:
            with st.spinner("Generating ideas..."):
                db = process_file(uploaded_file)
                context = get_context(db, topic)

                output = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{context}\n10 ideas for {topic}"}]
                )

                increment_usage(st.session_state.user)
                st.write(output.choices[0].message.content)
                logger.info(f"Ideas generated for: {topic}")
        except Exception as e:
            logger.error(f"Error generating ideas: {e}")
            st.error(f"Error generating ideas: {str(e)[:100]}")

# ---------------- PROFILE ----------------
elif page == "Profile":
    st.title("👤 Profile")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Username: {st.session_state.user}")
    with col2:
        st.write(f"Email: {st.session_state.email}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

