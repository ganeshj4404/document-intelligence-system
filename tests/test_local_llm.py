from app.services.llm_service import generate_response


prompt = """
Explain document summarization in exactly 3 bullet points.
Keep the answer simple.
"""


response = generate_response(prompt)

print("\n===== LOCAL LLM RESPONSE =====\n")
print(response)