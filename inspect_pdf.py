from pypdf import PdfReader
import sys

filename = "docs/CQRS_Architecting_for_Performance_and_Scale.pdf"

try:
    reader = PdfReader(filename)
    print(f"Pages: {len(reader.pages)}")
    
    total_text = ""
    for i, p in enumerate(reader.pages):
        text = p.extract_text()
        if text:
            print(f"--- Page {i+1} ---")
            print(text[:200]) # Print first 200 chars
            total_text += text
        else:
            print(f"--- Page {i+1}: [NO TEXT EXTRACTED] ---")
            
    print(f"\nTotal Text Length: {len(total_text)}")
except Exception as e:
    print(f"Error: {e}")
