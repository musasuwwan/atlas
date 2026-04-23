import os
import re
import json
from datetime import datetime
from core.config import WRANGLER_CMD, DEFAULT_CF_PROJECT, DEPLOY_RECORD_FILE
from utils.helpers import safe_subprocess, get_user_confirmation


def _wrangler() -> str:
    return WRANGLER_CMD if os.path.exists(WRANGLER_CMD) else "wrangler"


def run() -> str:
    wrangler = _wrangler()
    cwd = os.getcwd()

    project_name = DEFAULT_CF_PROJECT
    try:
        entered = input(f"Project name [{project_name}]: ").strip()
        if entered:
            project_name = entered
    except (EOFError, KeyboardInterrupt):
        return "Deployment cancelled."

    print(f"\n  Deploying '{project_name}' to Cloudflare Pages...")

    if not get_user_confirmation("Confirm deploy? (yes/no): "):
        return "Deployment cancelled."

    # Attempt project creation (ignored if already exists)
    safe_subprocess([wrangler, "pages", "project", "create", project_name], input="main\n")

    try:
        result = safe_subprocess([wrangler, "pages", "deploy", cwd, f"--project-name={project_name}"])
    except FileNotFoundError:
        return "Wrangler not found. Run: npm install -g wrangler"

    if result.returncode != 0:
        err = (result.stderr or result.stdout).strip()
        return f"Deployment failed: {err}"

    output = result.stdout + result.stderr
    match = re.search(r"https://[\w\-]+\.pages\.dev\S*", output)
    url = match.group(0).rstrip(".") if match else f"https://{project_name}.pages.dev"

    try:
        with open(os.path.join(cwd, DEPLOY_RECORD_FILE), "w") as f:
            json.dump({"project": project_name, "url": url, "timestamp": datetime.now().isoformat()}, f)
    except OSError:
        pass

    return f"Deployed. Live at {url}"
