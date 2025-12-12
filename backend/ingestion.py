import os
import uuid
import re
from typing import List, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from .models import Chunk, DocumentMetadata
from .config import settings

class IngestionService:
    def _clean_text(self, text: str) -> str:
        # Remove null bytes and excessive whitespace
        text = text.replace('\x00', '')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_pages(self, file_path: str, filename: str) -> List[Tuple[str, int]]:
        """
        Returns a list of (text, page_number).
        For non-paginated formats (txt, docx), returns [(text, 1)].
        """
        ext = os.path.splitext(filename)[1].lower()
        pages = []

        try:
            if ext == '.pdf':
                reader = PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    raw_text = page.extract_text()
                    if raw_text:
                        clean_text = self._clean_text(raw_text)
                        if len(clean_text) > 10:  # Skip empty or very short garbage pages
                            pages.append((clean_text, i + 1))
            
            elif ext == '.docx':
                doc = DocxDocument(file_path)
                # DOCX doesn't have strict pages, treat as one block or para-based?
                # Treating as single page for simplicity, or we could chunk by paragraphs etc.
                full_text = "\n".join([para.text for para in doc.paragraphs])
                clean_text = self._clean_text(full_text)
                if len(clean_text) > 10:
                    pages.append((clean_text, 1))

            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_text = f.read()
                    clean_text = self._clean_text(full_text)
                    if len(clean_text) > 10:
                        pages.append((clean_text, 1))
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            raise e
            
        return pages

    def chunk_text(self, text: str, filename: str, doc_id: str, page_num: int, start_idx: int) -> List[Chunk]:
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_len = len(text)
        
        # If text is smaller than chunk size, just one chunk
        if text_len <= chunk_size:
            meta = DocumentMetadata(
                filename=filename,
                chunk_index=start_idx,
                doc_id=doc_id,
                page=page_num
            )
            chunks.append(Chunk(
                id=f"{doc_id}-{start_idx}",
                text=text,
                metadata=meta
            ))
            return chunks

        idx = start_idx
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_slice = text[start:end]
            
            meta = DocumentMetadata(
                filename=filename,
                chunk_index=idx,
                doc_id=doc_id,
                page=page_num
            )
            
            chunks.append(Chunk(
                id=f"{doc_id}-{idx}",
                text=chunk_slice,
                metadata=meta
            ))
            
            start += chunk_size - overlap
            idx += 1
            
        return chunks

    def process_document(self, file_path: str, filename: str) -> List[Chunk]:
        doc_id = str(uuid.uuid4())
        pages = self._extract_pages(file_path, filename)
        
        all_chunks = []
        global_idx = 0
        
        for text, page_num in pages:
            page_chunks = self.chunk_text(text, filename, doc_id, page_num, global_idx)
            all_chunks.extend(page_chunks)
            global_idx += len(page_chunks)
            
        print(f"Processed {filename}: {len(pages)} pages, {len(all_chunks)} chunks.")
        return all_chunks

ingestion_service = IngestionService()
