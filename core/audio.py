import os
import tempfile
import wave
from elevenlabs import ElevenLabs
from core.config import ELEVENLABS_API_KEY, VOICE_ID, VOICE_MODEL


class AudioSystem:
    """Handles text-to-speech and playback using winsound (Windows built-in)"""

    def __init__(self):
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    def _convert_mp3_to_wav(self, mp3_path):
        """Convert MP3 to WAV using pydub"""
        from pydub import AudioSegment
        sound = AudioSegment.from_mp3(mp3_path)
        wav_path = mp3_path.replace('.mp3', '.wav')
        sound.export(wav_path, format="wav")
        return wav_path

    def _play_audio(self, audio_bytes):
        """Play audio using winsound (Windows built-in, no popup)"""
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_mp3.write(audio_bytes)
        temp_mp3.close()

        try:
            wav_path = self._convert_mp3_to_wav(temp_mp3.name)

            if os.name == 'nt':
                import winsound
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)

            try:
                os.unlink(temp_mp3.name)
                os.unlink(wav_path)
            except:
                pass

            return True

        except Exception as e:
            print(f"[ERROR] Audio playback failed: {e}")
            return False

    def speak(self, text):
        """Generate speech and play it"""
        try:
            audio = self.client.text_to_speech.convert(
                voice_id=VOICE_ID,
                model_id=VOICE_MODEL,
                text=text
            )

            audio_bytes = b"".join(audio)
            success = self._play_audio(audio_bytes)

            if not success:
                print(f"[ATLAS]: {text}")

        except Exception as e:
            print(f"[ERROR] Speech generation failed: {e}")
            print(f"[ATLAS]: {text}")


_audio = AudioSystem()


def speak(text: str) -> None:
    _audio.speak(text)
