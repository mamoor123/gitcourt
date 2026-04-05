#!/usr/bin/env python3
"""
GitCourt — AI Code Review Tribunal

Usage:
    python gitcourt.py <github-pr-url> [--provider openai|ollama|anthropic]

Or after pip install:
    gitcourt <github-pr-url>
    python -m gitcourt <github-pr-url>
"""

import os
import sys

# Allow running as `python gitcourt.py` from the repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gitcourt.cli import main

if __name__ == "__main__":
    main()
