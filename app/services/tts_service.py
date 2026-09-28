import asyncio
import re
from pathlib import Path

import edge_tts


DEFAULT_VOICE = "en-US-AriaNeural"
DEFAULT_RATE = "-5%"
DEFAULT_VOLUME = "+0%"
DEFAULT_PITCH = "+0Hz"


def prepare_text_for_speech(text: str) -> str:
    """
    Prepare extracted/generated text for more natural speech.

    This does not change the meaning of the text.
    It only improves spacing, pauses, and sentence endings.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace bullet symbols with a simple spoken-friendly marker.
    text = re.sub(r"(?m)^\s*[•●▪◦]\s*", "- ", text)

    # Clean excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph breaks
    lines = text.split("\n")

    prepared_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            prepared_lines.append("")
            continue

        # Avoid adding punctuation to lines that already have it.
        if not re.search(r"[.!?,;:]$", line):
            line += "."

        prepared_lines.append(line)

    text = "\n".join(prepared_lines)

    # Avoid too many consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


async def _generate_speech(
    text,
    output_file,
    voice=DEFAULT_VOICE,
    rate=DEFAULT_RATE,
    volume=DEFAULT_VOLUME,
    pitch=DEFAULT_PITCH,
):
    """
    Generate natural-sounding speech from text
    and save it as an MP3 file.
    """

    speech_text = prepare_text_for_speech(text)

    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )

    await communicate.save(str(output_file))


def generate_speech(
    text,
    output_file,
    voice=DEFAULT_VOICE,
    rate=DEFAULT_RATE,
    volume=DEFAULT_VOLUME,
    pitch=DEFAULT_PITCH,
):
    """
    Synchronous wrapper for the async TTS function.
    """

    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    asyncio.run(
        _generate_speech(
            text=text,
            output_file=output_file,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
    )

    return output_file