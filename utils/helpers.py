import subprocess
import threading
from core.config import CONFIRMATION_TIMEOUT


def safe_subprocess(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    defaults = {"capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace"}
    return subprocess.run(args, **{**defaults, **kwargs})


def get_user_confirmation(prompt: str) -> bool:
    """Prompt for yes/no with CONFIRMATION_TIMEOUT second timeout. Returns False on timeout."""
    result = {"value": None}
    event = threading.Event()

    def _read():
        try:
            result["value"] = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            result["value"] = ""
        event.set()

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    timed_out = not event.wait(timeout=CONFIRMATION_TIMEOUT)

    if timed_out:
        print(f"\n[No response in {CONFIRMATION_TIMEOUT}s — auto-cancelled]")
        return False

    return result["value"] in {"yes", "y"}


def format_section(title: str, lines: list[str]) -> str:
    body = "\n".join(f"  {l}" for l in lines)
    return f"{title}:\n{body}"
