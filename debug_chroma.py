import chromadb
from backend.config import settings

def inspect_db():
    print(f"Connecting to DB at: {settings.CHROMA_DB_PATH}")
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    try:
        coll = client.get_collection("rag_collection")
        count = coll.count()
        print(f"Total chunks in DB: {count}")
        
        if count > 0:
            peek = coll.peek(limit=3)
            print("\n--- Metadata Sample ---")
            for m in peek['metadatas']:
                print(m)
            
            print("\n--- Text Sample ---")
            for d in peek['documents']:
                print(d[:200] + "...")
        else:
            print("Collection is empty!")
            
    except Exception as e:
        print(f"Error accessing collection: {e}")

if __name__ == "__main__":
    inspect_db()
