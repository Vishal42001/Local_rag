# 🧠 RAG One

The ultimate **Local AI Knowledge Engine**. Chat with your documents using a premium, privacy-first RAG pipeline.

![RAG One UI](/api/placeholder/800/400) <!-- Add a screenshot later -->

## ✨ Premium Features
*   **🌑 Dark Black Glass UI**: A professional, distraction-free interface inspired by high-end SaaS tools.
*   **🌊 Fluid Streaming**: Real-time token generation for a responsive chat experience.
*   **🧠 Hybrid Search**: Combines **Vector Search** (ChromaDB) with **Cross-Encoder Reranking** (MS-MARCO) for pinpoint accuracy.
*   **🗣️ Voice Mode**: Listen to AI responses directly in the browser.
*   **⚡ Async Core**: Non-blocking architecture handles heavy indexing and thinking without freezing.
*   **🔒 100% Local**: Powered by **Ollama**. No data leaves your machine.

## 🚀 Quick Start

### Prerequisites
1.  **Ollama**: Must be installed and running.
    ```bash
    ollama serve
    ollama pull gemma2:2b
    ```

### Running Locally
1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Engine** (Backend + Frontend)
    ```bash
    # Terminal 1: Backend
    uvicorn backend.server:app --port 8000

    # Terminal 2: Frontend
    streamlit run app.py
    ```

### Running with Docker 🐳
```bash
docker-compose up --build
```
Access the app at `http://localhost:8501`.

## 🛠️ Stack
*   **Frontend**: Streamlit + Custom CSS + JS Particles
*   **Backend**: FastAPI (Async)
*   **Vector DB**: ChromaDB
*   **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
*   **LLM**: Ollama (`gemma2:2b`, `phi3`, etc.)

---
*Built with ❤️ by your AI Copilot.*

