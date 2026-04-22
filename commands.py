import re
import subprocess
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

_api_key = os.getenv("ANTHROPIC_API_KEY")
if not _api_key:
    raise EnvironmentError("ANTHROPIC_API_KEY not found in .env")

anthropic = Anthropic(api_key=_api_key)

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
    cwd = os.getcwd()
    try:
        project_name = input("Enter project name for deployment (e.g., 'atlas-demo'): ").strip()
    except (EOFError, KeyboardInterrupt):
        return "Deployment cancelled."

    if not project_name:
        return "No project name provided. Deployment cancelled."

    wrangler_cmd = "C:\\Users\\musam\\AppData\\Roaming\\npm\\wrangler.cmd"
    if not os.path.exists(wrangler_cmd):
        wrangler_cmd = "wrangler"

    try:
        subprocess.run(
            [wrangler_cmd, "pages", "project", "create", project_name],
            input="main\n",
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
    except FileNotFoundError:
        return "Wrangler CLI not found. Install with: npm install -g wrangler"

    try:
        result = subprocess.run(
            [wrangler_cmd, "pages", "deploy", cwd, "--project-name=" + project_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
    except FileNotFoundError:
        return "Wrangler CLI not found. Install with: npm install -g wrangler"

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        return f"Deployment failed: {error}"

    output = result.stdout + result.stderr
    url_match = re.search(r"https://[\w\-]+\.pages\.dev\S*", output)
    url = url_match.group(0).rstrip(".") if url_match else f"https://{project_name}.pages.dev"

    deploy_record = {
        "project": project_name,
        "url": url,
        "timestamp": datetime.now().isoformat(),
    }
    deploy_file = os.path.join(os.getcwd(), ".atlas_last_deploy")
    try:
        with open(deploy_file, "w") as f:
            json.dump(deploy_record, f)
    except OSError:
        pass

    return f"Deployed successfully. Live at {url}"


def execute_status() -> str:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch.returncode != 0:
        return "Git error: not a git repository."

    branch_name = branch.stdout.strip()

    porcelain = _run(["git", "status", "--porcelain"])
    change_count = len([l for l in porcelain.stdout.splitlines() if l.strip()])

    last_commit = _run(["git", "log", "-1", "--pretty=%B"])
    last_commit_msg = last_commit.stdout.strip() or "No commits yet"

    deploy_file = os.path.join(os.getcwd(), ".atlas_last_deploy")
    if os.path.exists(deploy_file):
        try:
            with open(deploy_file) as f:
                record = json.load(f)
            cf_lines = (
                f"- Last deployment: {record.get('project', 'unknown')}\n"
                f"  - URL: {record.get('url', 'unknown')}"
            )
        except (OSError, json.JSONDecodeError):
            cf_lines = "- Last deployment: error reading deploy file"
    else:
        cf_lines = "- Last deployment: No deployments yet"

    return (
        f"Git Status:\n"
        f"- Branch: {branch_name}\n"
        f"- Uncommitted changes: {change_count} file{'s' if change_count != 1 else ''}\n"
        f"- Last commit: {last_commit_msg}\n"
        f"\nCloudflare Status:\n"
        f"{cf_lines}"
    )
