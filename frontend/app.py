import streamlit as st
import requests
import json

# API configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Document Portal - AI Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Document Portal with AI Assistant")
st.markdown("Upload your documents and ask questions about their content!")

# Sidebar for document upload
with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=['pdf', 'txt']
    )
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                files = {"file": uploaded_file}
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error(f"Error: {response.text}")
    
    st.markdown("---")
    st.markdown("### Supported Formats")
    st.markdown("- PDF files")
    st.markdown("- TXT files")

# Main content area for chat
st.header("💬 Chat with Your Documents")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.caption(f"Sources: {', '.join(message['sources'])}")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": prompt}
                )
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    sources = result["sources"]
                    st.markdown(answer)
                    if sources:
                        st.caption(f"Sources: {', '.join(sources)}")
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error("Failed to get response from AI")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Clear chat button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()