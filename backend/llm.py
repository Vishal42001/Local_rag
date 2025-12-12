import requests
import json
from .config import settings

class LLMClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.DEFAULT_LLM_MODEL

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a comprehensive response (blocking).
        """
        # ... reuse existing logic or call stream and join ...
        return "".join(self.generate_response_stream(prompt, system_prompt))

    def generate_response_stream(self, prompt: str, system_prompt: str = None):
        """
        Generator that yields chunks of the response.
        """
        url = f"{self.base_url}/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        try:
            with requests.post(url, json=payload, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        body = json.loads(line)
                        if "message" in body and "content" in body["message"]:
                            yield body["message"]["content"]
                        if body.get("done", False):
                            break
        except Exception as e:
            print(f"LLM Stream Error: {e}")
            yield f"Error: {e}"

llm_client = LLMClient()
