\# Project ATLAS



Voice-controlled automation assistant for M99 agency.



\## Status: Phase 1+2 Complete ✅



\### Phase 1: Voice Loop (Complete)

\- Keyboard input → Claude API (Sonnet 4.6) → George voice output

\- Continuous conversation loop

\- ElevenLabs TTS (George voice, British, JARVIS-like)



\### Phase 2: Task Automation (Complete)

Three working voice commands:



\*\*1. Git Commit\*\* (`atlas commit`)

\- Analyzes git diff

\- Generates conventional commit message via Claude API

\- Asks confirmation

\- Commits + pushes to GitHub

\- Speaks confirmation



\*\*2. Cloudflare Deploy\*\* (`atlas deploy`)

\- Prompts for project name

\- Deploys current directory to Cloudflare Pages via Wrangler

\- Requires manual project creation first: `wrangler pages project create <name>`

\- Speaks deployment confirmation



\*\*3. Status\*\* (`atlas status`)

\- Shows git status (branch, uncommitted files, last commit)

\- Shows last Cloudflare deployment (if any)

\- No confirmation needed, instant response



\## Stack

\- Python 3.14

\- Anthropic API (claude-sonnet-4-6)

\- ElevenLabs TTS (George voice)

\- Wrangler CLI (Cloudflare deployments)

\- Git (version control)



\## Files

\- `atlas.py` - Main orchestration loop

\- `commands.py` - Command detection and execution

\- `requirements.txt` - Dependencies

\- `.env` - API keys (gitignored)

\- `CLAUDE.md` - This file (project context)



\## Next Steps (Phase 1.5 + 2.5)

\- Real microphone input (Whisper API)

\- Wake word detection

\- Auto-create Cloudflare projects

\- Trusted mode (skip confirmations)

