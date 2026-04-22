\# Project ATLAS



\*\*What this is:\*\* Voice-controlled automation assistant for M99 agency.



\## Current Phase: 2 (MCP-style Integration)



Phase 1 complete: voice loop working (keyboard input → Claude API → George voice output).



\## Phase 2 Goals



Add voice commands that execute real tasks:

1\. Git operations: commit + push with AI-generated commit messages

2\. Cloudflare deployments via Wrangler CLI

3\. Status queries: git + deployment status



\## Architecture



Hybrid routing:

\- If user input matches a command pattern → execute the task (subprocess calls)

\- If user input is general conversation → send to Claude API for chat

\- Always speak confirmation after execution



\## Stack



\- Python 3.14

\- Anthropic API (claude-sonnet-4-6) for chat + commit message generation

\- ElevenLabs TTS (voice: George, id: JBFqnCBsd6RMkjVDRZzb)

\- Subprocess for git + wrangler CLI calls



\## File Structure



atlas/

├── atlas.py          # Main script

├── commands.py       # NEW: Command handlers for Phase 2

├── requirements.txt  # Dependencies

├── .env             # API keys (gitignored)

└── CLAUDE.md        # This file



\## Coding Style



\- Concise, no over-commenting

\- Separate command logic into commands.py (keep atlas.py clean)

\- Error handling: try/except with spoken error messages

\- Exit gracefully on Ctrl+C



\## Voice Commands (Phase 2)



| Command | Action |

|---------|--------|

| "atlas commit" / "atlas, commit this" | git add -A, AI commit message, git commit, git push |

| "atlas deploy" / "atlas, deploy to cloudflare" | wrangler deploy (or pages deploy) |

| "atlas status" | shows git status + last deployment |



\## Safety



\- Phase 2: Always ask confirmation before push/deploy (Y/N)

\- Phase 2.5 (polish): Add "trusted mode" that skips confirmations

