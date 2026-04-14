import google.generativeai as genai
from config import GEMINI_API_KEY

# Replace with your API Key
genai.configure(api_key=GEMINI_API_KEY)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)