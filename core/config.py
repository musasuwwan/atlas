import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"{key} not set in .env")
    return val


ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY: str = _require("ELEVENLABS_API_KEY")

VOICE_ID: str = "JBFqnCBsd6RMkjVDRZzb"
VOICE_MODEL: str = "eleven_turbo_v2_5"

AI_MODEL: str = "claude-sonnet-4-6"
AI_MAX_TOKENS: int = 512
AI_COMMIT_MAX_TOKENS: int = 128

WRANGLER_CMD: str = r"C:\Users\musam\AppData\Roaming\npm\wrangler.cmd"
DEFAULT_CF_PROJECT: str = "atlas-demo-v1"

CONFIRMATION_TIMEOUT: int = 30

DEPLOY_RECORD_FILE: str = ".atlas_last_deploy"
SPEECH_TEMP_FILE: Path = Path(os.getenv("TEMP", "/tmp")) / "atlas_speech.mp3"
