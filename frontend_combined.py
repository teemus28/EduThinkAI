"""
EduThink AI - Streamlit Frontend
--------------------------------
A light-themed, user-friendly UI that talks to the FastAPI backend
(chatbot + mind map generator).

Run with:
    streamlit run app.py

Make sure your FastAPI backend is running (default: http://localhost:8000)
"""

import streamlit as st
import requests

# =====================================================
# CONFIG
# =====================================================

BACKEND_URL = "https://eduthinkai-backend.onrender.com"

st.set_page_config(
    page_title="EduThink AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# CUSTOM CSS (light, card-based, Mapify-inspired)
# =====================================================

CUSTOM_CSS = """
<style>
    /* ---- Global ---- */
    .stApp {
        background-color: #F7F8FC;
    }
    #MainMenu, footer {visibility: hidden;}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #ECECF4;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* ---- Brand header ---- */
    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.5rem;
    }
    .brand-logo {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6C63FF, #A78BFA);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .brand-title {
        font-size: 22px;
        font-weight: 800;
        color: #1E1E2D;
        margin: 0;
    }

    /* ---- Hero header ---- */
    .hero-icon {
        width: 64px;
        height: 64px;
        border-radius: 18px;
        background: linear-gradient(135deg, #6C63FF, #8B7CF6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        margin: 0 auto 14px auto;
        box-shadow: 0 8px 20px rgba(108, 99, 255, 0.25);
    }
    .hero-title {
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        color: #1E1E2D;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        text-align: center;
        color: #8A8AA3;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* ---- Cards ---- */
    .eduthink-card {
        background: #FFFFFF;
        border: 1px solid #ECECF4;
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 4px 14px rgba(30, 30, 45, 0.04);
    }

    /* ---- Chat bubbles ---- */
    .chat-bubble-user {
        background: #6C63FF;
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 6px 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 15px;
    }
    .chat-bubble-bot {
        background: #F0F0FA;
        color: #1E1E2D;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 6px 0;
        max-width: 80%;
        font-size: 15px;
    }

    /* ---- Mode toggle pills ---- */
    div[data-testid="stRadio"] > div {
        background: #F0F0FA;
        padding: 6px;
        border-radius: 14px;
        gap: 4px;
    }
    div[data-testid="stRadio"] label {
        background: transparent;
        border-radius: 10px;
        padding: 8px 18px !important;
        font-weight: 600;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        background-color: #6C63FF;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #5A52E0;
        color: white;
    }

    /* ---- Uploader ---- */
    div[data-testid="stFileUploader"] section {
        border: 1.5px dashed #C9C6F7;
        border-radius: 14px;
        background: #FAFAFF;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"bot", "content": str}

if "mindmap_result" not in st.session_state:
    st.session_state.mindmap_result = None

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-logo">🧠</div>
            <p class="brand-title">EduThink AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("AI-Powered Educational Toolkit")
    st.divider()

    mode = st.radio(
        "Choose a tool",
        options=["💬 Chatbot", "🗺️ Mind Map Generator"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Backend")
    st.code(BACKEND_URL, language=None)

    with st.expander("⚙️ Settings"):
        backend_input = st.text_input("Backend URL", value=BACKEND_URL)
        if backend_input:
            BACKEND_URL = backend_input

    st.divider()
    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ---- Social / Contact links (replace with your own URLs) ----
    LINKEDIN_URL = "https://www.linkedin.com/in/sumeet-sahu-529557291/"
    GITHUB_URL = "https://github.com/teemus28"

    st.divider()
    st.caption("Connect with me")
    st.markdown(
        f"""
        <div style="display:flex; gap:10px; margin-top:4px;">
            <a href="{LINKEDIN_URL}" target="_blank" style="text-decoration:none;">
                <div style="display:flex; align-items:center; gap:6px;
                            background:#F0F0FA; padding:8px 14px; border-radius:10px;
                            color:#1E1E2D; font-weight:600; font-size:14px;">
                    🔗 LinkedIn
                </div>
            </a>
            <a href="{GITHUB_URL}" target="_blank" style="text-decoration:none;">
                <div style="display:flex; align-items:center; gap:6px;
                            background:#F0F0FA; padding:8px 14px; border-radius:10px;
                            color:#1E1E2D; font-weight:600; font-size:14px;">
                    🐙 GitHub
                </div>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================
# HERO HEADER
# =====================================================

if mode == "💬 Chatbot":
    icon, title, subtitle = "💬", "Ask Anything", \
        "Your RAG-powered study buddy for notes, PDFs, and images."
else:
    icon, title, subtitle = "🗺️", "Mind Map Generator", \
        "Turn any document into a structured, visual mind map."

st.markdown(f'<div class="hero-icon">{icon}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-title">{title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-subtitle">{subtitle}</div>', unsafe_allow_html=True)

# =====================================================
# CHATBOT MODE
# =====================================================

if mode == "💬 Chatbot":

    st.markdown('<div class="eduthink-card">', unsafe_allow_html=True)

    # ---- Chat history ----
    chat_container = st.container(height=380)
    with chat_container:
        if not st.session_state.messages:
            st.info("Start the conversation below — ask a question, or attach an image for context.")
        for msg in st.session_state.messages:
            css_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-bot"
            st.markdown(
                f'<div class="{css_class}">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.write("")

    # ---- Input row ----
    col_img, col_text, col_send = st.columns([1, 5, 1])

    with col_img:
        uploaded_image = st.file_uploader(
            "Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed",
            key="chat_image_uploader"
        )

    with col_text:
        user_query = st.text_input(
            "Message", placeholder="Type your question...",
            label_visibility="collapsed", key="chat_query_input"
        )

    with col_send:
        send_clicked = st.button("Send ➤", use_container_width=True)

    if uploaded_image is not None:
        st.caption(f"📎 Attached: {uploaded_image.name}")

    if send_clicked and user_query.strip():
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.spinner("EduThink AI is thinking..."):
            try:
                files = None
                if uploaded_image is not None:
                    files = {"image": (uploaded_image.name, uploaded_image.getvalue())}

                response = requests.post(
                    f"{BACKEND_URL}/chatbot/chat",
                    data={"query": user_query},
                    files=files,
                    timeout=120,
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "No response received.")
                else:
                    answer = f"⚠️ Error {response.status_code}: {response.text}"

            except requests.exceptions.ConnectionError:
                answer = "⚠️ Could not connect to backend. Is the FastAPI server running?"
            except Exception as e:
                answer = f"⚠️ Something went wrong: {e}"

        st.session_state.messages.append({"role": "bot", "content": answer})
        st.rerun()

    elif send_clicked and not user_query.strip():
        st.warning("Please type a question before sending.")

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# MIND MAP MODE
# =====================================================

else:

    st.markdown('<div class="eduthink-card">', unsafe_allow_html=True)

    st.markdown("##### 📄 Upload a document or image")
    st.caption("Supported formats: PDF, TXT, JPG, JPEG, PNG, WEBP. "
               "Images are read using visual AI (great for diagrams, notes, or photos of text).")

    uploaded_file = st.file_uploader(
        "Upload document or image",
        type=["pdf", "txt", "jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="mindmap_file_uploader",
    )

    if uploaded_file is not None and uploaded_file.type and uploaded_file.type.startswith("image/"):
        st.image(uploaded_file, caption="Preview", width=220)

    generate_clicked = st.button("✨ Generate Mind Map", use_container_width=False)

    if generate_clicked:
        if uploaded_file is None:
            st.warning("Please upload a document first.")
        else:
            with st.spinner("Analyzing document and building your mind map..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue())
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/mindmap/generate",
                        files=files,
                        timeout=300,
                    )

                    if response.status_code == 200:
                        st.session_state.mindmap_result = response.json()
                        st.success("Mind map generated successfully!")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        st.session_state.mindmap_result = None

                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Could not connect to backend. Is the FastAPI server running?")
                except Exception as e:
                    st.error(f"⚠️ Something went wrong: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Result section ----
    result = st.session_state.mindmap_result
    if result and result.get("success"):
        st.write("")
        st.markdown('<div class="eduthink-card">', unsafe_allow_html=True)
        st.markdown("##### 🗺️ Your Mind Map")

        download_url = f"{BACKEND_URL}{result.get('download_url', '')}"

        tab_preview, tab_tree = st.tabs(["Interactive Preview", "Tree Structure"])

        with tab_preview:
            try:
                html_resp = requests.get(download_url, timeout=60)
                if html_resp.status_code == 200:
                    st.components.v1.html(html_resp.text, height=600, scrolling=True)
                else:
                    st.warning("Preview unavailable. Use the download link below instead.")
            except Exception:
                st.warning("Preview unavailable. Use the download link below instead.")

            st.link_button("⬇️ Download Mind Map (HTML)", download_url, use_container_width=False)

        with tab_tree:
            st.json(result.get("tree", {}))

        st.markdown('</div>', unsafe_allow_html=True)
