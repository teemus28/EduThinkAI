import streamlit as st
import requests

# ----------------------------
# Configuration
# ----------------------------

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ----------------------------
# CSS
# ----------------------------

st.markdown("""
<style>

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

.block-container{
padding-top:1.5rem;
max-width:900px;
}

.user-msg{
background:#DCF8C6;
padding:12px;
border-radius:12px;
margin-bottom:10px;
}

.bot-msg{
background:#F1F3F4;
padding:12px;
border-radius:12px;
margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Session State
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Header
# ----------------------------

st.title("🤖 RAG Chatbot")

st.caption("Powered by Gemma-3 + FAISS")

# ----------------------------
# Sidebar
# ----------------------------

# with st.sidebar:

#     st.header("Options")

#     uploaded_image = st.file_uploader(
#         "Upload Image (Optional)",
#         type=["png","jpg","jpeg"]
#     )

#     if st.button("🗑 Clear Chat", use_container_width=True):
#         st.session_state.messages = []
#         st.rerun()
uploaded_image = st.file_uploader(
    "📷 Upload Image (Optional)",
    type=["png", "jpg", "jpeg"]
)

# ----------------------------
# Display Chat
# ----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("image") is not None:
            st.image(message["image"], width=250)

# ----------------------------
# Chat Input
# ----------------------------

prompt = st.chat_input("Ask anything...")

if prompt:

    # Display User
    with st.chat_message("user"):

        st.markdown(prompt)

        if uploaded_image:
            st.image(uploaded_image, width=250)

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt,
            "image":uploaded_image
        }
    )

    files = {}

    if uploaded_image:

        files["image"] = (
            uploaded_image.name,
            uploaded_image.getvalue(),
            uploaded_image.type
        )

    data = {
        "query":prompt
    }

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    API_URL,
                    data=data,
                    files=files if files else None,
                    timeout=300
                )

                if response.status_code == 200:

                    answer = response.json()["answer"]

                else:

                    answer = f"❌ Error: {response.text}"

            except Exception as e:

                answer = str(e)

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )