import os
import json
from core.config import DEPLOY_RECORD_FILE
from utils.helpers import safe_subprocess, format_section


def run() -> str:
    branch = safe_subprocess(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch.returncode != 0:
        return "Git error: not a git repository."

    porcelain = safe_subprocess(["git", "status", "--porcelain"])
    change_count = len([l for l in porcelain.stdout.splitlines() if l.strip()])

    last_commit = safe_subprocess(["git", "log", "-1", "--pretty=%B"])
    last_msg = last_commit.stdout.strip() or "No commits yet"

    git_section = format_section("Git", [
        f"Branch: {branch.stdout.strip()}",
        f"Uncommitted changes: {change_count} file{'s' if change_count != 1 else ''}",
        f"Last commit: {last_msg}",
    ])

    deploy_file = os.path.join(os.getcwd(), DEPLOY_RECORD_FILE)
    if os.path.exists(deploy_file):
        try:
            with open(deploy_file) as f:
                record = json.load(f)
            cf_lines = [
                f"Project: {record.get('project', 'unknown')}",
                f"URL: {record.get('url', 'unknown')}",
                f"Deployed: {record.get('timestamp', 'unknown')}",
            ]
        except (OSError, json.JSONDecodeError):
            cf_lines = ["Error reading deploy record"]
    else:
        cf_lines = ["No deployments yet"]

    cf_section = format_section("Cloudflare", cf_lines)
    return f"{git_section}\n\n{cf_section}"
