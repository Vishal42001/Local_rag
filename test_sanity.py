import requests

def test_json():
    url = "http://127.0.0.1:8000/api/query"
    payload = {
        "query": "test",
        "messages": []
    }
    print(f"Connecting to {url}...")
    try:
        # Note: NOT stream=True
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_json()
