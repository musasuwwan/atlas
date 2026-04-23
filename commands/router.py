import re
from commands import git, cloudflare, status

_PATTERNS: dict[str, re.Pattern] = {
    "commit": re.compile(r"\bcommit\b", re.IGNORECASE),
    "deploy": re.compile(r"\bdeploy\b", re.IGNORECASE),
    "status": re.compile(r"\bstatus\b", re.IGNORECASE),
}


def detect(user_input: str) -> str | None:
    for name, pattern in _PATTERNS.items():
        if pattern.search(user_input):
            return name
    return None


def execute(command: str) -> str:
    if command == "commit":
        return git.run()
    if command == "deploy":
        return cloudflare.run()
    if command == "status":
        return status.run()
    return f"Unknown command: {command}"
