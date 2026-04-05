#!/usr/bin/env python3
"""
GitCourt — AI Code Review Tribunal
Three agents debate your PR. The Judge delivers the verdict.
"""

import argparse
import json
import os
import sys
import time

from .utils.github_fetcher import fetch_pr_diff, fetch_pr_info
from .agents.prosecutor import Prosecutor
from .agents.defender import Defender
from .agents.judge import Judge
from .utils.formatter import (
    print_banner,
    print_case_header,
    print_agent_argument,
    print_verdict,
    print_score_bar,
    print_separator,
)


def parse_args():
    from . import __version__

    parser = argparse.ArgumentParser(
        description="GitCourt — AI Code Review Tribunal"
    )
    parser.add_argument("pr_url", help="GitHub Pull Request URL")
    parser.add_argument(
        "--version",
        action="version",
        version=f"gitcourt {__version__}",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "ollama", "anthropic"],
        default=os.getenv("GITCOURT_PROVIDER", "openai"),
        help="LLM provider (default: openai, or set GITCOURT_PROVIDER)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name (default: provider-specific)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (or set OPENAI_API_KEY / ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        help="Ollama server URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="LLM temperature (default: 0.7)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output verdict as JSON instead of pretty-printed",
    )
    return parser.parse_args()


def get_default_model(provider: str) -> str:
    defaults = {
        "openai": "gpt-4o",
        "ollama": "llama3.1",
        "anthropic": "claude-sonnet-4-20250514",
    }
    return defaults.get(provider, "gpt-4o")


def build_llm_config(args) -> dict:
    config = {
        "provider": args.provider,
        "model": args.model or get_default_model(args.provider),
        "temperature": args.temperature,
    }

    if args.provider == "openai":
        config["api_key"] = args.api_key or os.getenv("OPENAI_API_KEY")
        if not config["api_key"]:
            print("❌ Error: OPENAI_API_KEY not set. Use --api-key or set the env var.")
            sys.exit(1)
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        config["base_url"] = base_url.rstrip("/")

    elif args.provider == "anthropic":
        config["api_key"] = args.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not config["api_key"]:
            print("❌ Error: ANTHROPIC_API_KEY not set. Use --api-key or set the env var.")
            sys.exit(1)

    elif args.provider == "ollama":
        config["ollama_url"] = args.ollama_url.rstrip("/")

    return config


def call_llm(config: dict, system: str, user: str) -> str:
    """Call the configured LLM provider and return the response text."""

    if config["provider"] == "openai":
        import openai
        client = openai.OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
            timeout=120.0,
        )
        resp = client.chat.completions.create(
            model=config["model"],
            temperature=config["temperature"],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content

    elif config["provider"] == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=config["api_key"], timeout=120.0)
        resp = client.messages.create(
            model=config["model"],
            max_tokens=4096,
            temperature=config["temperature"],
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text

    elif config["provider"] == "ollama":
        import requests
        url = f"{config['ollama_url']}/api/chat"
        payload = {
            "model": config["model"],
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": config["temperature"]},
        }
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    else:
        raise ValueError(f"Unknown provider: {config['provider']}")


def main():
    args = parse_args()
    llm_config = build_llm_config(args)

    if not args.json_output:
        print_banner()

    # Fetch PR data
    if not args.json_output:
        print("📋 Fetching PR data...", end=" ", flush=True)

    try:
        pr_info = fetch_pr_info(args.pr_url)
        pr_diff = fetch_pr_diff(args.pr_url)
    except Exception as e:
        print(f"\n❌ Failed to fetch PR: {e}")
        sys.exit(1)

    if not args.json_output:
        print("✅")
        print_case_header(pr_info)

    # Truncate diff if too long (keep first ~12k chars for context)
    max_diff_chars = 12000
    truncated = False
    if len(pr_diff) > max_diff_chars:
        pr_diff = pr_diff[:max_diff_chars] + "\n\n... [diff truncated for analysis] ..."
        truncated = True

    # Escape triple backticks in diff to prevent code fence injection
    safe_diff = pr_diff.replace("```", "\\`\\`\\`")

    pr_context = f"""## PR Info
- **Title:** {pr_info['title']}
- **Author:** {pr_info['author']}
- **Repo:** {pr_info['repo']}
- **Description:** {pr_info.get('body', 'No description provided.')[:1000]}

## Diff
```diff
{safe_diff}
```"""

    # === PROSECUTION ===
    if not args.json_output:
        print("⚖️  Court is in session...\n")
        print_separator()
        print("🔴 THE PROSECUTION presents its case...\n")
        time.sleep(0.5)

    try:
        prosecutor = Prosecutor()
        prosecution = call_llm(
            llm_config,
            prosecutor.system_prompt(),
            prosecutor.user_prompt(pr_context),
        )
    except Exception as e:
        print(f"\n❌ LLM error during prosecution: {e}")
        sys.exit(1)

    if not prosecution:
        print("\n❌ LLM returned empty response during prosecution.")
        sys.exit(1)

    if not args.json_output:
        print_agent_argument("PROSECUTOR", "🔴", prosecution)

    # === DEFENSE ===
    if not args.json_output:
        print_separator()
        print("🔵 THE DEFENSE presents its case...\n")
        time.sleep(0.5)

    try:
        defender = Defender()
        defense = call_llm(
            llm_config,
            defender.system_prompt(),
            defender.user_prompt(pr_context, prosecution),
        )
    except Exception as e:
        print(f"\n❌ LLM error during defense: {e}")
        sys.exit(1)

    if not defense:
        print("\n❌ LLM returned empty response during defense.")
        sys.exit(1)

    if not args.json_output:
        print_agent_argument("DEFENDER", "🔵", defense)

    # === VERDICT ===
    if not args.json_output:
        print_separator()
        print("🟡 THE JUDGE deliberates...\n")
        time.sleep(0.5)

    try:
        judge = Judge()
        verdict_raw = call_llm(
            llm_config,
            judge.system_prompt(),
            judge.user_prompt(pr_context, prosecution, defense),
        )
    except Exception as e:
        print(f"\n❌ LLM error during verdict: {e}")
        sys.exit(1)

    if not verdict_raw:
        print("\n❌ LLM returned empty response during verdict.")
        sys.exit(1)

    # Parse verdict
    verdict = judge.parse_verdict(verdict_raw)

    if args.json_output:
        output = {
            "pr": pr_info,
            "prosecution": prosecution,
            "defense": defense,
            "verdict": verdict,
            "truncated_diff": truncated,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_separator()
        print_verdict(verdict)
        print_score_bar(verdict.get("score", 5))
        print()
        print(f"🏁 Case dismissed. Run another PR through the tribunal!")
        print(f"   github.com/{pr_info['repo']}/pull/{pr_info['number']}")
