import streamlit as st
import requests

# ----------------------------
# Configuration
# ----------------------------
API_URL = "http://backend:8000"  # Docker-safe service name

st.set_page_config(
    page_title="Document Portal - AI Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Document Portal with AI Assistant")
st.markdown("Upload documents and ask questions about them.")

# ----------------------------
# Safe session initialization
# ----------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ----------------------------
# Sidebar - Upload
# ----------------------------
with st.sidebar:
    st.header("📄 Upload Documents")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"]
    )

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": uploaded_file}
                )

                if response.ok:
                    st.success(response.json().get("message", "Uploaded"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Upload failed: {str(e)}")

# ----------------------------
# Chat UI
# ----------------------------
st.header("💬 Chat with Your Documents")

# render history safely
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(f"Sources: {', '.join(msg['sources'])}")

# ----------------------------
# Input
# ----------------------------
prompt = st.chat_input("Ask a question about your documents...")

if prompt:
    # store user message
    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/query",
                    json={"question": prompt}
                )

                if res.ok:
                    data = res.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        st.caption(f"Sources: {', '.join(sources)}")

                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error("Backend error")

            except Exception as e:
                st.error(f"Request failed: {str(e)}")

# ----------------------------
# Clear chat
# ----------------------------
if st.button("Clear Chat History"):
    st.session_state["messages"] = []
    st.rerun()