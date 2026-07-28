import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- AUTO-DISCOVERING ACTIVE MODELS ---")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY is missing in .env")
    exit()

client = genai.Client(api_key=api_key)

try:
    # 1. Fetch all models available for your exact API key
    print("1. Querying Google AI Studio for active models on your key...")
    available_models = []
    for m in client.models.list():
        # Get clean model name string (e.g. gemini-2.5-flash)
        name = m.name.replace("models/", "")
        available_models.append(name)
        print(f"   Found Model: {name}")

    if not available_models:
        print("❌ No models returned for this key!")
        exit()

    # 2. Pick the first candidate model and test generation
    print("\n2. Testing models for text generation...")
    success = False
    
    for model_name in available_models:
        if "gemini" not in model_name or "embedding" in model_name:
            continue
            
        print(f"\nTrying model: '{model_name}'...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Answer in 5 words: What is Zetech University?",
            )
            print("✅ SUCCESS!")
            print(f"Working Model Name: {model_name}")
            print(f"Response: {response.text.strip()}")
            success = True
            break
        except Exception as e:
            print(f"❌ Failed for {model_name}: {e}")

    if not success:
        print("\n❌ Could not find a model with available free tier quota.")

except Exception as e:
    print(f"\n❌ Error during discovery: {e}")