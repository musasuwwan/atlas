import os
import sys
import tempfile
from pathlib import Path
from anthropic import Anthropic
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from commands import detect_command, execute_git_commit, confirm_and_push, execute_deploy, execute_status

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

SYSTEM_PROMPT = (
    "You are ATLAS, a voice-controlled automation assistant for M99 agency. "
    "Keep responses concise and conversational — you're speaking aloud, not writing essays."
)

conversation: list[dict] = []


def speak(text: str) -> None:
    voice_id = "JBFqnCBsd6RMkjVDRZzb"
    print(f"[ATLAS using voice: George - {voice_id}]")
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_turbo_v2_5",
    )
    temp_path = Path(tempfile.gettempdir()) / "atlas_speech.mp3"
    with open(temp_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    os.startfile(str(temp_path))


def chat(user_input: str) -> str:
    conversation.append({"role": "user", "content": user_input})
    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=conversation,
    )
    reply = response.content[0].text
    conversation.append({"role": "assistant", "content": reply})
    return reply


def handle_commit() -> str:
    status_msg, commit_msg = execute_git_commit()
    if commit_msg is None:
        return status_msg

    print(f"\nATLAS: {status_msg}")
    speak(status_msg)

    try:
        confirmation = input("Confirm commit? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "Commit cancelled."

    if confirmation in {"yes", "y"}:
        result = confirm_and_push(commit_msg)
    else:
        result = "Commit cancelled."

    return result


def handle_deploy() -> str:
    print("\nATLAS: Deploy current directory to Cloudflare Pages?")
    speak("Deploy to Cloudflare?")

    try:
        confirmation = input("Confirm deploy? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "Deployment cancelled."

    if confirmation in {"yes", "y"}:
        return execute_deploy()
    return "Deployment cancelled."


def main() -> None:
    print("ATLAS online. Type 'quit' or 'exit' to stop.")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nATLAS offline.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("ATLAS offline.")
            sys.exit(0)

        command = detect_command(user_input)

        try:
            if command == "commit":
                reply = handle_commit()
            elif command == "deploy":
                reply = handle_deploy()
            elif command == "status":
                reply = execute_status()
            else:
                reply = chat(user_input)

            print(f"ATLAS: {reply}")
            speak(reply)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
