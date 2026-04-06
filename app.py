from dotenv import load_dotenv
import os
import streamlit as st
from groq import Groq
from streamlit_option_menu import option_menu

# LangChain imports (fixed)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

# Load env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Content Pro+", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user == "admin" and pwd == "vip123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- SIDEBAR ----------------
from streamlit_option_menu import option_menu

with st.sidebar:
    page = option_menu(
        menu_title="AI Content Pro",
        options=["Dashboard", "Instagram", "YouTube", "Ideas","Logout"],
        icons=["house", "instagram", "youtube", "lightbulb","box-arrow-right"],
        menu_icon="rocket",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#0f172a"},
            "icon": {"color": "#38bdf8", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "border-radius": "10px",
            },
            "nav-link-selected": {
                "background-color": "#2563eb",
                "color": "white",
                "font-weight": "bold",
            },
        }
        
    )
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
# ---------------- RAG HELPER ----------------
def process_file(uploaded_file):
    if uploaded_file:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        loader = PyPDFLoader("temp.pdf")
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
    st.title("📊 Main Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Instagram Posts", "24", "+5 today")

    with col2:
        st.metric("YouTube Videos", "10", "+2 today")

    with col3:
        st.metric("Ideas Generated", "56", "+12 today")

    st.markdown("---")

    st.subheader("📌 Recent Activity")
    st.write("✔ Generated Instagram caption")
    st.write("✔ Uploaded YouTube script")
    st.write("✔ Created new content idea")

# ---------------- INSTAGRAM ----------------
elif page == "Instagram":
    st.title("📸 Instagram Content Generator")

    topic = st.text_input("Enter topic")

    uploaded_file = st.file_uploader("Upload context (optional PDF)", type="pdf")

    if st.button("Generate Content"):
        db = process_file(uploaded_file)
        context = get_context(db, topic)

        # Agent workflow
        hooks = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\n5 viral hooks for {topic}"}]
        ).choices[0].message.content

        caption = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nInstagram caption for {topic}"}]
        ).choices[0].message.content

        hashtags = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nHashtags for {topic}"}]
        ).choices[0].message.content

        st.subheader("🔥 Hooks")
        st.write(hooks)

        st.subheader("📄 Caption")
        st.write(caption)

        st.subheader("🏷️ Hashtags")
        st.write(hashtags)

# ---------------- YOUTUBE ----------------
elif page == "YouTube":
    st.title("🎬 YouTube Generator")

    topic = st.text_input("Enter topic")

    uploaded_file = st.file_uploader("Upload context (optional PDF)", type="pdf")

    if st.button("Generate"):
        db = process_file(uploaded_file)
        context = get_context(db, topic)

        output = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nWrite YouTube script for {topic}"}]
        )

        st.write(output.choices[0].message.content)

# ---------------- IDEAS ----------------
elif page == "Ideas":
    st.title("💡 Content Ideas Generator")

    topic = st.text_input("Enter topic")

    uploaded_file = st.file_uploader("Upload context (optional PDF)", type="pdf")

    if st.button("Generate Ideas"):
        db = process_file(uploaded_file)
        context = get_context(db, topic)

        output = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"{context}\nGenerate 10 content ideas for {topic}"}]
        )

        st.write(output.choices[0].message.content)

# ---------------- Logout ----------------
elif page == "Logout":
    st.session_state.logged_in = False
    st.rerun()