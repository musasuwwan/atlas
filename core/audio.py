import os
from elevenlabs.client import ElevenLabs
from core.config import ELEVENLABS_API_KEY, VOICE_ID, VOICE_MODEL, SPEECH_TEMP_FILE

_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def _play(path: str) -> None:
    try:
        from playsound import playsound
        playsound(path)
    except Exception:
        os.startfile(path)


def speak(text: str) -> None:
    try:
        audio = _client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=VOICE_MODEL,
        )
        with open(SPEECH_TEMP_FILE, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        _play(str(SPEECH_TEMP_FILE))
    except Exception as e:
        print(f"[audio error: {e}]")
