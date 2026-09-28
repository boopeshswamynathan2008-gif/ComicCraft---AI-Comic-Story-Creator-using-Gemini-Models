import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit()

client = genai.Client(api_key=api_key)

models = [
    "gemini-3.8-flash",
    "gemini-3.1-pro-preview",
]

for model in models:
    print("\n" + "=" * 50)
    print("Testing:", model)

    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with only: TEST OK"
        )

        print("✅ ACCESS WORKS")
        print("Response:", response.text)

    except Exception as e:
        print("❌ FAILED")
        print(type(e).__name__)
        print(e)