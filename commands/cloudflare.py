import os
import re
import json
from datetime import datetime
from core.audio import speak
from core.config import WRANGLER_CMD, DEFAULT_CF_PROJECT, DEPLOY_RECORD_FILE
from utils.helpers import get_user_confirmation


class Cloudflare:
    def deploy(self):
        """Deploy to Cloudflare Pages with project name input"""
        speak("Starting Cloudflare deployment process.")

        # Ask for project name
        print(f"\nDefault project: {DEFAULT_CF_PROJECT}")
        project_input = input("Enter project name (or press Enter for default): ").strip()
        project_name = project_input if project_input else DEFAULT_CF_PROJECT

        speak(f"Deploying to project: {project_name}")

        # Show what will be deployed
        print(f"\nProject: {project_name}")
        print(f"Directory: {os.getcwd()}")

        # Confirm
        speak("Ready to deploy. Do you want to proceed?")
        confirmed = get_user_confirmation("Deploy to Cloudflare Pages?")

        if not confirmed:
            speak("Deployment cancelled.")
            return False

        # Deploy
        speak("Deploying now. This may take a moment.")

        wrangler = WRANGLER_CMD if os.path.exists(WRANGLER_CMD) else "wrangler"
        import subprocess
        result = subprocess.run(
            [wrangler, "pages", "deploy", ".", f"--project-name={project_name}"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            speak(f"Deployment failed. {result.stderr}")
            print(f"[ERROR] {result.stderr}")
            return False

        url = self._extract_url(result.stdout + result.stderr)
        self._save_deployment_record(project_name, url)

        if url:
            speak(f"Deployment successful! Your site is live at {url}")
            print(f"\n✓ Live at: {url}\n")
        else:
            speak("Deployment successful! Check your Cloudflare dashboard for the URL.")

        return True

    def _extract_url(self, output: str) -> str:
        match = re.search(r"https://[\w\-]+\.pages\.dev\S*", output)
        return match.group(0).rstrip(".") if match else ""

    def _save_deployment_record(self, project_name: str, url: str) -> None:
        try:
            record_path = os.path.join(os.getcwd(), DEPLOY_RECORD_FILE)
            with open(record_path, "w") as f:
                json.dump(
                    {"project": project_name, "url": url, "timestamp": datetime.now().isoformat()},
                    f,
                )
        except OSError:
            pass


def run() -> str:
    cf = Cloudflare()
    success = cf.deploy()
    return "Deployment complete." if success else "Deployment cancelled or failed."
