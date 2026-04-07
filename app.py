import os
import uuid
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from streamlit_option_menu import option_menu
from passlib.context import CryptContext

# LangChain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

# ---------------- ENV ----------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Content Pro+", layout="wide")

#--------------STYLE----------------
# st.markdown("""
# <style>
# [data-testid="stAppViewContainer"] {
#     background-color:rgba(47, 68, 116, 1);
#     color: black;
# }

#     div[data-testid="stTextInput"] input {
#         background-color: lightwhite;
#         color: white;
#         border-radius: 8px;
#         border: 1px solid black;
#         padding: 10px;
#     }
# </style>
# """, unsafe_allow_html=True)

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
def create_user(username,email, password):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    try:
        hashed_pw = pwd_context.hash(password)

        c.execute(
            "INSERT INTO users (username,email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        return True

    except Exception as e:
        print("Signup error:", e)
        return False

    finally:
        conn.close()


def login_user(username,email, password):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()

    c.execute("SELECT username,email,password FROM users WHERE username=? or email=?", (username, email))
    data = c.fetchone()
    
    conn.close()

    if data:
        st.session_state.user = data[0]
        st.session_state.email = data[1]
        return pwd_context.verify(password, data[2])
    

    return False

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
            if create_user(username,email, password):
                st.success("✅ Account created! Please login.")
            else:
                st.error("❌ Username already exists")

    else:
        if st.button("Login", use_container_width=True):
            if login_user(username,email, password):
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
def process_file(uploaded_file):
    if uploaded_file:
        file_path = f"temp_{uuid.uuid4()}.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings()
        db = FAISS.from_documents(chunks, embeddings)

        return db
    return None


def get_context(db, query):
    if db:
        results = db.similarity_search(query, k=2)
        return "\n".join([r.page_content for r in results])
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
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True):
                st.session_state.show_upgrade = True
            st.stop()

        db = process_file(uploaded_file)
        context = get_context(db, topic)

        output = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nInstagram content for {topic}"}]
        )

        increment_usage(st.session_state.user)
        st.write(output.choices[0].message.content)

# ---------------- YOUTUBE ----------------
elif page == "YouTube":
    st.title("🎬 YouTube Generator")

    topic = st.text_input("Enter topic", placeholder="Enter video idea...")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if st.button("Generate", use_container_width=True):
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True,disabled=True):
                st.session_state.show_upgrade = True
            st.stop()

        db = process_file(uploaded_file)
        context = get_context(db, topic)

        output = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nYouTube script for {topic}"}]
        )

        increment_usage(st.session_state.user)
        st.write(output.choices[0].message.content)

# ---------------- IDEAS ----------------
elif page == "Ideas":
    st.title("💡 Ideas Generator")

    topic = st.text_input("Enter topic", placeholder="Enter niche or topic...")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if st.button("Generate Ideas", use_container_width=True):
        if get_usage(st.session_state.user) >= LIMIT:
            st.error("🚫 Limit reached")
            if st.button("💳 Upgrade Plan", use_container_width=True):
                st.session_state.show_upgrade = True

            st.stop()
        
        db = process_file(uploaded_file)
        context = get_context(db, topic)

        output = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\n10 ideas for {topic}"}]
        )

        increment_usage(st.session_state.user)
        st.write(output.choices[0].message.content)

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

