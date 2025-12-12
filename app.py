import streamlit as st
import requests
import json
import base64
import os

# API Configuration
API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="3D Knowledge Chat",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Asset Injection ---
def load_css():
    with open("static/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_js():
    with open("static/particles.js", "r") as f:
        particles_js = f.read()
    with open("static/speech.js", "r") as f:
        speech_js = f.read()
        
    # Combine and inject
    js_code = f"""
    <script>
    {particles_js}
    {speech_js}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

load_css()
load_js()

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🧠 RAG One")
    st.markdown("<div class='glass-card' style='font-size: 0.9em;'>Upload your PDFs or Docs to instantly chat with them using local AI.</div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Knowledge", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        if st.button("✨ Ingest Document", use_container_width=True):
            with st.spinner("Processing..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    res = requests.post(f"{API_URL}/upload", files=files)
                    if res.status_code == 200:
                        st.success("Indexing Complete!")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    st.markdown("---")
    st.markdown("### ⚙️ Systems")
    if st.button("🗑️ Reset Memory", use_container_width=True):
        try:
            requests.delete(f"{API_URL}/reset")
            st.success("Core memory wiped.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed: {e}")
            
    # Voice Trigger
    if st.button("🗣️ Read Response", use_container_width=True):
        # We need to trigger JS from Python. Streamlit doesn't support direct JS calls easily.
        # We use a hack: render an iframe that runs the script then disappears.
        st.components.v1.html("<script>parent.window.speakLastResponse()</script>", height=0, width=0)
        
    model = st.selectbox("Model", ["gemma2:2b", "gemma2", "phi3", "llama3", "mistral"])
    st.caption("Running locally on 127.0.0.1")


# --- Landing Page / Chat UI ---
if not st.session_state.messages:
    # Hero Section (Modern Website feel)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-top: 50px;'>RAG One</h1>", unsafe_allow_html=True)
        st.markdown("<div class='hero-subtitle'>Your private, high-performance AI knowledge engine.</div>", unsafe_allow_html=True)
        
        # Feature Grid
        st.markdown("""
        <div class='glass-card'>
            <div style='display: flex; justify-content: space-between; text-align: center;'>
                <div style='flex: 1;'>
                    <div style='font-size: 2rem;'>🌊</div>
                    <div style='font-weight: bold; margin-top: 5px;'>Fluid Streaming</div>
                    <div style='font-size: 0.8em; color: gray;'>Real-time token generation</div>
                </div>
                <div style='flex: 1; border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1);'>
                    <div style='font-size: 2rem;'>🧠</div>
                    <div style='font-weight: bold; margin-top: 5px;'>Hybrid Ranking</div>
                    <div style='font-size: 0.8em; color: gray;'>Vectors + Cross-Encoding</div>
                </div>
                <div style='flex: 1;'>
                    <div style='font-size: 2rem;'>🛡️</div>
                    <div style='font-weight: bold; margin-top: 5px;'>Private Core</div>
                    <div style='font-size: 0.8em; color: gray;'>100% Local Execution</div>
                </div>
            </div>
            <br>
            <div style='text-align: center; font-size: 0.9em; color: #666;'>
                Supported formats: PDF, DOCX, TXT • Powered by Ollama
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat History layer
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='chat-message-user'>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message-bot'>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Citations
            if "citations" in msg and msg["citations"]:
                with st.expander(f"📚 References ({len(msg['citations'])})"):
                    for cite in msg["citations"]:
                        st.markdown(f"""
                        <div class='citation-box'>
                           <div style="font-weight: bold; margin-bottom: 4px;">{cite['filename']}</div>
                           <div style="font-size: 0.9em; opacity: 0.8;">"{cite['excerpt'][:150]}..."</div>
                           <div style="font-size: 0.7em; opacity: 0.6; margin-top: 4px;">Page {cite.get('page_number', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Ask the crystal ball..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Rerun to show user message immediately (visual trick)
    st.rerun()

# Processing Logic (runs on rerun)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]["content"]
    
    with st.empty():
        st.markdown("<div class='typing-dot'></div><div class='typing-dot'></div><div class='typing-dot'></div>", unsafe_allow_html=True)
        
        try:
            # Prepare history
            clean_history = []
            for m in st.session_state.messages[:-1]:
                clean_history.append({"role": m["role"], "content": m["content"]})

            req_body = {
                "query": last_msg,
                "model": model,
                "messages": clean_history
            }
            
            # Placeholder for citations using a mutable container
            stream_state = {"citations": []}

            def stream_generator():
                with requests.post(f"{API_URL}/query", json=req_body, stream=True) as r:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "citations" in data:
                                    stream_state["citations"] = data["citations"]
                                elif "chunk" in data:
                                    yield data["chunk"]
                                elif "status" in data:
                                    # Show status toast or log
                                    print(f"Status: {data['status']}")
                                    # Optional: st.toast(data['status']) - but tricky inside generator
                            except:
                                pass

            # Stream the response
            with st.chat_message("assistant"):
                response_text = st.write_stream(stream_generator())
                
                # Show citations after stream
                citations = stream_state["citations"]
                if citations:
                    with st.expander(f"📚 References ({len(citations)})"):
                        for cite in citations:
                            st.markdown(f"""
                            <div class='citation-box'>
                               <div style="font-weight: bold; margin-bottom: 4px;">{cite['filename']}</div>
                               <div style="font-size: 0.9em; opacity: 0.8;">"{cite['excerpt'][:150]}..."</div>
                               <div style="font-size: 0.7em; opacity: 0.6; margin-top: 4px;">Page {cite.get('page_number', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "citations": stream_state["citations"]
            })
            
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {e}"
            })
            st.rerun()
