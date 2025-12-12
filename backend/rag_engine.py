import json
from typing import List
from starlette.concurrency import run_in_threadpool
import asyncio

from .vector_store import vector_store
from .embeddings import embedding_model
from .llm import llm_client
from .models import QueryResponse, RetrievalResult
from .config import settings

from sentence_transformers import CrossEncoder

# Lazy load global variable
_reranker = None

class RAGEngine:
    async def query_stream(self, user_query: str, history: List[dict] = []):
        """
        Async Generator for RAG response.
        """
        print("DEBUG: Entered Async query_stream")
        yield json.dumps({"status": "DEBUG: Stream Connection Established"}) + "\n"
        
        # Yield start status
        yield json.dumps({"status": "🧠 Contextualizing query..."}) + "\n"

        # 0. Contextualize
        standalone_query = user_query
        if history:
            try:
                history_str = ""
                for msg in history[-4:]:
                    history_str += f"{msg['role']}: {msg['content']}\n"
                
                rewrite_prompt = (
                    f"Given the following conversation history and a follow-up question, "
                    f"rewrite the follow-up question to be a standalone question that captures all context. "
                    f"Do NOT answer the question, just rewrite it.\n\n"
                    f"Chat History:\n{history_str}\n"
                    f"Follow-up Question: {user_query}\n\n"
                    f"Standalone Question:"
                )
                
                # Wrapper for LLM call
                def run_rewrite():
                    return llm_client.generate_response(rewrite_prompt).strip()
                
                standalone_query = await run_in_threadpool(run_rewrite)
            except Exception as e:
                print(f"Rewrite error: {e}")

        # 1. Embed & Retrieve
        yield json.dumps({"status": "🔍 Searching documents..."}) + "\n"
        
        # Determine K and Initial K
        target_k = settings.TOP_K_RETRIEVAL
        initial_k = target_k * 3
        
        # Embed (Blocking)
        def run_embed():
            return embedding_model.generate([standalone_query])[0]
        emb = await run_in_threadpool(run_embed)
        
        # Retrieve (Blocking)
        def run_query():
            return vector_store.query(emb, top_k=initial_k)
        candidate_docs = await run_in_threadpool(run_query)
        
        # 2. Rerank (Try/Except)
        retrieved_docs = candidate_docs
        try:
            yield json.dumps({"status": "⚖️ Reranking results..."}) + "\n"
            
            # Load Reranker (Blocking)
            global _reranker
            if _reranker is None:
                def load_model():
                    global _reranker
                    print("Loading CrossEncoder...")
                    _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                    return _reranker
                await run_in_threadpool(load_model)
                
            if candidate_docs:
                def run_predict(query, docs):
                    pairs = [[query, doc.excerpt] for doc in docs]
                    return _reranker.predict(pairs)
                
                scores = await run_in_threadpool(run_predict, standalone_query, candidate_docs)
                
                for i, doc in enumerate(candidate_docs):
                    doc.score = float(scores[i])
                candidate_docs.sort(key=lambda x: x.score, reverse=True)
                retrieved_docs = candidate_docs[:target_k]
        except Exception as e:
            print(f"Reranking failed (fallback to vector search): {e}")
            retrieved_docs = candidate_docs[:target_k]

        # Yield Citations
        yield json.dumps({"citations": [d.model_dump() for d in retrieved_docs]}) + "\n"
        yield json.dumps({"status": "✨ Generating answer..."}) + "\n"

        # 3. Context
        context_block = ""
        for doc in retrieved_docs:
            context_block += f"-- Source: {doc.filename} (Page {doc.page})\n{doc.excerpt}\n\n"
        
        if not context_block.strip():
            context_block = "No relevant context found."

        # 4. Prompt
        system_prompt = (
            "You are an expert AI assistant. Your goal is to provide comprehensive, detailed, and well-explained answers based on the context. "
            "Do not be brief. Elaborate on the key points, provide examples from the text if available, and ensure the answer is thorough. "
            "Answer based ONLY on the provided context."
        )
        full_history_str = ""
        for msg in history[-6:]:
            full_history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

        full_prompt = f"""Context:
{context_block}

Chat History:
{full_history_str}

User Question: {user_query}

Answer:"""

        # 5. Stream
        # Iterate sync generator, yielding control to keep event loop alive
        for chunk in llm_client.generate_response_stream(full_prompt, system_prompt=system_prompt):
            yield json.dumps({"chunk": chunk}) + "\n"
            await asyncio.sleep(0)


rag_engine = RAGEngine()
