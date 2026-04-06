from dotenv import load_dotenv
import os
from groq import Groq
import streamlit as st
from streamlit_option_menu import option_menu

# Load env
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page config
st.set_page_config(page_title="AI Content Pro", page_icon="🚀", layout="wide")

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login to AI Content Pro")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "vip123":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    selected = option_menu(
        "AI Content Pro",
        ["Dashboard", "Instagram", "YouTube", "Hooks", "Ideas"],
        icons=["house", "instagram", "youtube", "lightning", "bulb"],
        menu_icon="cast",
        default_index=0,
    )

# ---------------- DASHBOARD ----------------
if selected == "Dashboard":
    st.title("🚀 AI Content Dashboard")
    
    st.markdown("### Grow Faster with AI")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Content Generated", "120+")
    col2.metric("Active Users", "12")
    col3.metric("Growth Rate", "🔥 High")

# ---------------- INSTAGRAM ----------------
elif selected == "Instagram":
    st.title("📸 Instagram Caption Generator")
    
    topic = st.text_input("Enter your topic")

    if st.button("Generate Caption"):
        prompt = f"""
        Create a viral Instagram caption for: {topic}
        
        Include:
        - Hook
        - Value
        - CTA
        - Hashtags
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a viral Instagram content expert."},
                {"role": "user", "content": prompt}
            ]
        )

        st.success(response.choices[0].message.content)

# ---------------- YOUTUBE ----------------
elif selected == "YouTube":
    st.title("🎬 YouTube Script Generator")
    
    topic = st.text_input("Enter video topic")

    if st.button("Generate Script"):
        prompt = f"""
        Write a YouTube script for: {topic}
        
        Include:
        - Hook
        - Main content
        - CTA
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a YouTube growth expert."},
                {"role": "user", "content": prompt}
            ]
        )

        st.success(response.choices[0].message.content)

# ---------------- HOOKS ----------------
elif selected == "Hooks":
    st.title("⚡ Viral Hooks Generator")
    
    topic = st.text_input("Enter topic")

    if st.button("Generate Hooks"):
        prompt = f"Generate 10 viral hooks for: {topic}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a viral marketing expert."},
                {"role": "user", "content": prompt}
            ]
        )

        st.success(response.choices[0].message.content)

# ---------------- IDEAS ----------------
elif selected == "Ideas":
    st.title("💡 Content Ideas Generator")
    
    topic = st.text_input("Enter niche/topic")

    if st.button("Generate Ideas"):
        prompt = f"Generate 10 high-engagement content ideas for: {topic}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a content strategist."},
                {"role": "user", "content": prompt}
            ]
        )

        st.success(response.choices[0].message.content)