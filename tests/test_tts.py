from app.services.tts_service import generate_speech


text = """
The company experienced significant growth in 2025.
The IT division contributed 55 percent of total revenue.
Revenue increased by 18 percent compared to 2024.
Net profit reached 4.2 crore rupees.
"""


output_file = "data/audio/test_summary.mp3"


print("===== TTS TEST =====")
print("Generating speech...")

result = generate_speech(
    text,
    output_file
)

print(f"\nAudio saved to: {result}")