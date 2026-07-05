import streamlit as st
import requests
import time

# ------------------- CONFIG -------------------
API_BASE_URL = "http://127.0.0.1:8000"
GENERATE_ENDPOINT = f"{API_BASE_URL}/generate"

st.set_page_config(
    page_title="AI Mind Map Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- STYLING -------------------
st.markdown("""
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #4ecdc4;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #999;
            margin-bottom: 2rem;
        }
        .status-box {
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .success-box {
            background-color: rgba(78, 205, 196, 0.1);
            border-left: 4px solid #4ecdc4;
        }
        .error-box {
            background-color: rgba(255, 107, 107, 0.1);
            border-left: 4px solid #ff6b6b;
        }
        div.stButton > button {
            background-color: #4ecdc4;
            color: black;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #3db8af;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
for key, default in {
    "tree": None,
    "download_url": None,
    "html_file": None,
    "history": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("### ⚙️ Backend Status")
    st.markdown("---")

    try:
        health = requests.get(API_BASE_URL, timeout=2)
        st.success("✅ Backend connected")
    except requests.exceptions.RequestException:
        st.error("❌ Backend not reachable")
        st.caption(f"Start it with:\n`uvicorn app:app --reload`")

    st.markdown("---")
    st.markdown("### 📄 Supported Files")
    st.caption("PDF, TXT, JPG, JPEG, PNG, WEBP")

    st.markdown("---")
    st.markdown("### 🕘 Recent Files")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            st.caption(f"• {item}")
    else:
        st.caption("No files processed yet")

    st.markdown("---")
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.tree = None
        st.session_state.download_url = None
        st.session_state.html_file = None
        st.rerun()

# ------------------- HEADER -------------------
st.markdown('<div class="main-header">🧠 AI Mind Map Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Upload a PDF, image, or text file — Gemma-3 will turn it into an interactive mind map.</div>',
    unsafe_allow_html=True
)

# ------------------- FILE UPLOAD -------------------
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "jpg", "jpeg", "png", "webp"]
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button(
        "🚀 Generate Mind Map",
        use_container_width=True,
        disabled=(uploaded_file is None)
    )

# ------------------- PROCESS FILE -------------------
if generate_btn and uploaded_file is not None:
    with st.spinner("Extracting content and generating mind map... this may take a minute for large files."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

            start_time = time.time()
            response = requests.post(GENERATE_ENDPOINT, files=files, timeout=300)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    st.session_state.tree = data["tree"]
                    st.session_state.html_file = data["html_file"]
                    st.session_state.download_url = data["download_url"]
                    st.session_state.history.append(uploaded_file.name)

                    st.markdown(
                        f'<div class="status-box success-box">✅ Mind map generated in {elapsed:.1f}s</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="status-box error-box">❌ Generation failed: {data}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f'<div class="status-box error-box">❌ Backend error ({response.status_code}): {response.text}</div>',
                    unsafe_allow_html=True
                )

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Make sure FastAPI is running:\n\n`uvicorn app:app --reload`")
        except requests.exceptions.Timeout:
            st.error("Request timed out. The file may be too large — try a smaller document.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ------------------- DISPLAY RESULTS -------------------
if st.session_state.tree and st.session_state.download_url:
    st.markdown("---")

    mindmap_full_url = f"{API_BASE_URL}{st.session_state.download_url}"

    tab1, tab2, tab3 = st.tabs(["🗺️ Mind Map", "📋 Tree Structure (JSON)", "⬇️ Export"])

    with tab1:
        st.components.v1.iframe(mindmap_full_url, height=700, scrolling=True)
        st.caption(f"File: `{st.session_state.html_file}`")

    with tab2:
        st.json(st.session_state.tree)

    with tab3:
        col_a, col_b = st.columns(2)

        with col_a:
            import json
            st.download_button(
                label="Download JSON",
                data=json.dumps(st.session_state.tree, indent=2),
                file_name="mindmap_structure.json",
                mime="application/json",
                use_container_width=True
            )

        with col_b:
            try:
                html_resp = requests.get(mindmap_full_url, timeout=10)
                st.download_button(
                    label="Download HTML",
                    data=html_resp.content,
                    file_name=st.session_state.html_file,
                    mime="text/html",
                    use_container_width=True
                )
            except Exception:
                st.caption("HTML download unavailable")

else:
    st.markdown("---")
    st.info("👆 Upload a file and click **Generate Mind Map** to get started.")