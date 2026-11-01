from google import genai

from swasthya_setu.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

resp = client.models.generate_content(
    model=settings.gemini_model,
    contents="Dengue ke 3 symptoms Hindi mein batao, short mein.",
)
print(resp.text)