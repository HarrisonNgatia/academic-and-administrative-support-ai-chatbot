import os
import requests
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class GeminiFallbackHandler:
    def __init__(self, api_key: str = None):
        # Automatically reads GEMINI_API_KEY from environment/.env
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        self.system_context = (
            "You are an AI Academic Support Assistant for Zetech University. "
            "Provide concise, polite, and actionable answers to student queries."
        )

    def get_fallback_response(self, prompt: str) -> str:
        if not self.api_key:
            return "System Notice: Gemini API Key is missing."

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Context: {self.system_context}\nStudent Query: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 200}
        }
        headers = {"Content-Type": "application/json"}

        try:
            res = requests.post(self.endpoint_url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            return "I am unable to resolve that specific query at the moment."
        except Exception as e:
            print(f"[Gemini Exception]: {e}")
            return "Connection error with generative support module."