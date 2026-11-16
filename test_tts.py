import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv(
    dotenv_path=Path("backend") / ".env",
    override=True
)

client = ElevenLabs(
    api_key=os.environ["ELEVENLABS_API_KEY"]
)

print("Testing ElevenLabs voice...")

audio = client.text_to_speech.convert(
    voice_id=os.environ["ELEVENLABS_VOICE_ID"],
    model_id="eleven_flash_v2_5",
    output_format="mp3_44100_128",
    text="Hello! Welcome to the doctor appointment assistant."
)

with open("test_voice.mp3", "wb") as file:
    for chunk in audio:
        file.write(chunk)

print("SUCCESS! Audio generated: test_voice.mp3")