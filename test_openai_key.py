from dotenv import load_dotenv
import os
import openai

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
print("Loaded key:", key[:8] + "..." + key[-4:] if key else None)
client = openai.OpenAI(api_key=key)
try:
    models = client.models.list()
    print("Models:", [m.id for m in models.data])
except Exception as e:
    print("OpenAI error:", e) 