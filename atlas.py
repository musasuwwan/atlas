import sys
from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY, AI_MODEL, AI_MAX_TOKENS
from core.audio import speak
from commands.router import detect, execute

_client = Anthropic(api_key=ANTHROPIC_API_KEY)
_SYSTEM = (
    "You are ATLAS, a voice-controlled automation assistant for M99 agency. "
    "Keep responses concise and conversational — you're speaking aloud, not writing essays."
)
_history: list[dict] = []


def _chat(text: str) -> str:
    _history.append({"role": "user", "content": text})
    response = _client.messages.create(
        model=AI_MODEL,
        max_tokens=AI_MAX_TOKENS,
        system=_SYSTEM,
        messages=_history,
    )
    reply = response.content[0].text
    _history.append({"role": "assistant", "content": reply})
    return reply


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

        command = detect(user_input)
        try:
            reply = execute(command) if command else _chat(user_input)
        except Exception as e:
            reply = f"Something went wrong: {e}"

        print(f"\nATLAS: {reply}")
        speak(reply)


if __name__ == "__main__":
    main()
