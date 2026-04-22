import re
import subprocess
import os
from anthropic import Anthropic

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_COMMAND_PATTERNS = {
    "commit": re.compile(r"\bcommit\b", re.IGNORECASE),
    "deploy": re.compile(r"\bdeploy\b", re.IGNORECASE),
    "status": re.compile(r"\bstatus\b", re.IGNORECASE),
}


def detect_command(user_input: str) -> str | None:
    for command, pattern in _COMMAND_PATTERNS.items():
        if pattern.search(user_input):
            return command
    return None


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def execute_git_commit() -> tuple[str, str | None]:
    """Returns (status_message, proposed_commit_message).
    If no changes or error, commit_message is None."""
    status = _run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        return f"Git error: {status.stderr.strip() or 'not a git repository'}", None
    if not status.stdout.strip():
        return "No changes to commit.", None

    diff_cached = _run(["git", "diff", "--cached"])
    diff_unstaged = _run(["git", "diff"])
    diff_text = (diff_cached.stdout + diff_unstaged.stdout).strip()

    if not diff_text:
        diff_text = status.stdout.strip()

    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=128,
            messages=[{
                "role": "user",
                "content": (
                    "Generate a single conventional commit message (e.g. 'feat: add voice command routing') "
                    "for the following git diff. Output only the commit message, nothing else.\n\n"
                    f"{diff_text[:4000]}"
                ),
            }],
        )
        commit_msg = response.content[0].text.strip().strip('"').strip("'")
    except Exception as e:
        return f"Failed to generate commit message: {e}", None

    return f"Proposed commit: {commit_msg}", commit_msg


def confirm_and_push(commit_msg: str) -> str:
    add = _run(["git", "add", "-A"])
    if add.returncode != 0:
        return f"git add failed: {add.stderr.strip()}"

    commit = _run(["git", "commit", "-m", commit_msg])
    if commit.returncode != 0:
        return f"git commit failed: {commit.stderr.strip()}"

    push = _run(["git", "push"])
    if push.returncode != 0:
        return f"Committed locally, but push failed: {push.stderr.strip()}"

    return f"Done. Committed and pushed: {commit_msg}"


def execute_deploy() -> str:
    return "Not implemented yet — coming in Phase 2 Part 2."


def execute_status() -> str:
    return "Not implemented yet — coming in Phase 2 Part 3."
