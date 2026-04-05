#!/usr/bin/env python3
"""
GitCourt — AI Code Review Tribunal

Usage:
    python gitcourt.py <github-pr-url> [--provider openai|ollama|anthropic]

Or after pip install:
    gitcourt <github-pr-url>
    python -m gitcourt <github-pr-url>
"""

from gitcourt.cli import main

if __name__ == "__main__":
    main()
