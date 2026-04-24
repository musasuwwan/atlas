from anthropic import Anthropic
from core.audio import speak
from core.config import ANTHROPIC_API_KEY, AI_MODEL, AI_COMMIT_MAX_TOKENS
from utils.helpers import safe_subprocess, get_user_confirmation

_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _generate_commit_message(diff: str) -> str:
    response = _client.messages.create(
        model=AI_MODEL,
        max_tokens=AI_COMMIT_MAX_TOKENS,
        messages=[{
            "role": "user",
            "content": (
                "Generate a single conventional commit message (e.g. 'feat: add voice routing') "
                "for the following git diff. Output only the commit message, nothing else.\n\n"
                f"{diff[:4000]}"
            ),
        }],
    )
    return response.content[0].text.strip().strip('"').strip("'")


def run() -> str:
    status = safe_subprocess(["git", "status", "--porcelain"])
    if status.returncode != 0:
        return "Git error: not a git repository."
    if not status.stdout.strip():
        return "No changes to commit."

    diff = (
        safe_subprocess(["git", "diff", "--cached"]).stdout
        + safe_subprocess(["git", "diff"]).stdout
    ).strip() or status.stdout.strip()

    try:
        commit_msg = _generate_commit_message(diff)
    except Exception as e:
        return f"Could not generate commit message: {e}"

    print(f"\n  Proposed: {commit_msg}")

    speak(f"Proposed commit message: {commit_msg}")

    speak("Do you approve this commit message?")
    if not get_user_confirmation("Confirm commit? (yes/no): "):
        return "Commit cancelled."

    add = safe_subprocess(["git", "add", "-A"])
    if add.returncode != 0:
        return "Failed to stage changes."

    commit = safe_subprocess(["git", "commit", "-m", commit_msg])
    if commit.returncode != 0:
        return f"Commit failed: {commit.stderr.strip()}"

    push = safe_subprocess(["git", "push"])
    if push.returncode != 0:
        return f"Committed locally, but push failed: {push.stderr.strip()}"

    return f"Committed and pushed: {commit_msg}"
