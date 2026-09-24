import asyncio
from pathlib import Path

import edge_tts


DEFAULT_VOICE = "en-US-AriaNeural"


async def _generate_speech(text, output_file, voice=DEFAULT_VOICE):
    """
    Generate speech from text and save it as an MP3 file.
    """

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(str(output_file))


def generate_speech(text, output_file, voice=DEFAULT_VOICE):
    """
    Synchronous wrapper for the async TTS function.
    """

    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    asyncio.run(
        _generate_speech(
            text,
            output_file,
            voice
        )
    )

    return output_file