import requests
import json

def test_stream():
    url = "http://127.0.0.1:8000/api/stream-test"
    payload = {
        "query": "What is this document about?",
        "model": "gemma2:2b",
        "messages": []
    }
    
    print(f"Connecting to {url}...")
    try:
        with requests.post(url, json=payload, stream=True) as r:
            print(f"Status Code: {r.status_code}")
            try:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        print(f"Received: {line.decode('utf-8')[:100]}...")
            except Exception as e:
                print(f"Stream interrupted: {e}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_stream()
