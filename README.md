# ⚖️ GitCourt — AI Code Review Tribunal

> Three AI agents debate your Pull Request. The Judge delivers the verdict.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/providers-OpenAI_|_Anthropic_|_Ollama-green.svg" alt="Providers">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</p>

```
   ▄████ ▄▄▄█████▓ ██▀███   ▄▄▄       ▄████▄   ██▓ ███▄    █   ▄████
  ██▒ ▀█▒▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    ▒██▀ ▀█  ▓██▒ ██ ▀█   █  ██▒ ▀█▒
 ▒██░▄▄▄░▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
 ░▓█  ██▓░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄▄ ▒▓▓▄ ▄██▒░██░▓██▒  ▐▌██▒░▓█  ██▓
 ░▒▓███▀▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░░██░▒██░   ▓██░░▒▓███▀▒
  ░▒   ▒   ░ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒
   ░   ░     ░░     ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒    ▒ ░ ░ ░░   ░ ▒░  ░   ░
```

## What is this?

GitCourt takes any GitHub Pull Request and runs it through three AI agents:

- **🔴 The Prosecutor** — aggressively finds every bug, anti-pattern, and security issue
- **🔵 The Defender** — justifies the code, provides context, and counters the prosecution
- **🟡 The Judge** — weighs both sides and delivers a verdict with a score (1-10)

It's code review, but make it a courtroom drama.

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourname/gitcourt.git
cd gitcourt
pip install -r requirements.txt

# Run with OpenAI (default)
export OPENAI_API_KEY="sk-..."
python gitcourt.py https://github.com/torvalds/linux/pull/123

# Run with Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python gitcourt.py https://github.com/user/repo/pull/456 --provider anthropic

# Run 100% locally with Ollama (no API keys!)
ollama pull llama3.1
python gitcourt.py https://github.com/user/repo/pull/456 --provider ollama

# JSON output (for CI/CD integration)
python gitcourt.py https://github.com/user/repo/pull/456 --json
```

## Output

```
═══════════════════════════════════════════════════════════════════
  📋 CASE #1234: Add user authentication middleware
  Repo: acme/api-server | Author: @devguru
  Changes: +142 -23 (3 files)
═══════════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────────

  🔴 THE PROSECUTOR

  The prosecution submits that this code contains THREE serious
  violations of software engineering best practices...

  🔴 Charge 1: Hardcoded JWT secret on line 47
  ...

──────────────────────────────────────────────────────────────────

  🔵 THE DEFENDER

  The defense acknowledges the Prosecutor's passion but submits
  that context is everything...

──────────────────────────────────────────────────────────────────

  🟡 THE VERDICT

  "This court finds the defendant PR GUILTY of sloppy secrets
  management but INNOCENT of the performance charges..."

  Score: 6/10  [████████████████████░░░░░░░░░░░░░░░░░░]  NEEDS WORK 🔧
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--provider` | `openai`, `anthropic`, or `ollama` | `openai` |
| `--model` | Model name | Provider default |
| `--api-key` | API key (or use env vars) | — |
| `--ollama-url` | Ollama server URL | `http://localhost:11434` |
| `--temperature` | LLM temperature | `0.7` |
| `--json` | JSON output (for CI) | off |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GITHUB_TOKEN` | GitHub token (optional, for higher rate limits) |
| `OLLAMA_URL` | Ollama server URL |
| `GITCOURT_PROVIDER` | Default provider |

## CI/CD Integration

GitCourt can output JSON for pipeline integration:

```bash
python gitcourt.py $PR_URL --json > verdict.json

# Check the score
score=$(jq '.verdict.score' verdict.json)
if [ "$score" -lt 5 ]; then
  echo "GitCourt says: CHANGES REQUESTED (score: $score)"
  exit 1
fi
```

## Why?

Because regular code review is boring, and every dev secretly wants an AI to roast their code in a courtroom setting.

Also because:
- **Multi-perspective review** catches more issues than single-agent review
- **The debate format** surfaces nuanced trade-offs, not just "fix this"
- **The score** gives a quick signal for PR health
- **It's hilarious** and your team will actually use it

## How It Works

```
PR URL → GitHub API → Diff
                          ↓
              ┌───────────┼───────────┐
              ↓           ↓           ↓
         Prosecutor    Defender     (waiting)
         (find bugs)   (defend code)
              ↓           ↓
              └─────┬─────┘
                    ↓
              Judge (weigh arguments)
                    ↓
              Verdict + Score
```

Each agent gets the full PR diff plus the previous agent's arguments. The Prosecutor goes first, the Defender responds to the prosecution, and the Judge sees everything before ruling.

## License

MIT — fork it, ship it, go viral.
