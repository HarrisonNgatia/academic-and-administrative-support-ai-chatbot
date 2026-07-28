import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiFallbackHandler:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.system_context = (
            "You are an AI Academic Support Assistant for Zetech University. "
            "Provide concise, polite, and actionable answers to student queries."
        )

    def get_fallback_response(self, prompt: str) -> str:
        if not self.client:
            print("[Gemini Error]: GEMINI_API_KEY environment variable is missing.")
            return "System Notice: Gemini API Key is missing."

        full_prompt = f"System Context: {self.system_context}\nStudent Query: {prompt}"

        try:
            # Using the confirmed active model name for your key
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini Exception]: {e}")
            return "I am unable to resolve that specific query at the moment."