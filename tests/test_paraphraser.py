from app.services.paraphraser import paraphrase_text


text = """
The company experienced significant growth in 2025,
with the IT division contributing 55% of total revenue.
Revenue increased by 18% compared to 2024.
Net profit reached ₹4.2 crore and total revenue was ₹12 crore.
"""

print("===== PARAPHRASING TEST =====")

result = paraphrase_text(text)

print("\nORIGINAL:")
print(text)

print("\nPARAPHRASED:")
print(result)