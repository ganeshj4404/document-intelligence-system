from app.config import LLM_API_KEY
from openai import OpenAI


print("API key loaded:", bool(LLM_API_KEY))

client = OpenAI(api_key=LLM_API_KEY)

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Reply with exactly: LLM connection successful."
)

print("\n===== LLM RESPONSE =====")
print(response.output_text)
