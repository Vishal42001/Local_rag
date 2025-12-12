# 🔮 3D Multi-Document Knowledge Chat

A premium, local RAG application featuring a **3D Glassmorphism UI** (Streamlit) and a robust backend (FastAPI + ChromaDB + Ollama).

## Features
- **3D UI**: Physics-based particle background, neon glassmorphism effects.
- **Local RAG**: Runs entirely offline using Ollama and ChromaDB.
- **Ingestion**: Supports PDF, DOCX, TXT with automatic chunking.
- **Verification**: Citations provided for every answer.

## Prerequisites
1. **Ollama**: Must be installed and running.
   ```bash
   ollama serve
   ollama pull phi3:medium
   ```

## Quick Start (Local)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Backend**
   ```bash
   uvicorn backend.server:app --reload --port 8000
   ```

3. **Start Frontend** (in a new terminal)
   ```bash
   streamlit run app.py
   ```
   Open `http://localhost:8501` to view the 3D UI.

## Docker Start

```bash
docker-compose up --build
```
Access the app at `http://localhost:8501`.

## Configuration
Edit `.env` or `backend/config.py` to change models or paths.
Default LLM: `gemma2:2b` (can be changed in UI).
Default Embedder: `all-MiniLM-L6-v2`.

## Troubleshooting

### "Connection Refused"
- Ensure Ollama is running: `ollama serve`.
- Ensure Backend is running: `http://localhost:8000/docs`.

### "Model not found"
- Install the default model: `ollama pull gemma2:2b`.

### "No text could be extracted" / 400 Error
- The PDF is likely a **scanned image** or has no selectable text.
- **Solution**: Use an online OCR tool (like Adobe Acrobat or smallpdf) to convert it to a "Searchable PDF" before uploading.
- Text-based PDFs and `.docx` files work best.

### Python Version Issues
- This project requires **Python 3.10 - 3.12**.
- Python 3.14 (experimental) is NOT supported due to missing binary wheels for `onnxruntime` and `scipy`.

