"""GitHub PR fetcher — extracts diff and metadata from PR URLs."""

import os
import re

import requests


def parse_pr_url(url: str) -> dict:
    """Parse a GitHub PR URL into its components."""
    # Handle various URL formats:
    # https://github.com/owner/repo/pull/123
    # https://github.com/owner/repo/pull/123/
    # https://github.com/owner/repo/pull/123/files
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(
            f"Invalid GitHub PR URL: {url}\n"
            "Expected format: https://github.com/owner/repo/pull/123"
        )

    return {
        "owner": match.group(1),
        "repo": match.group(2),
        "number": int(match.group(3)),
    }


def fetch_pr_info(url: str) -> dict:
    """Fetch PR metadata using the GitHub API."""
    parts = parse_pr_url(url)
    api_url = (
        f"https://api.github.com/repos/{parts['owner']}/{parts['repo']}"
        f"/pulls/{parts['number']}"
    )

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitCourt/1.0",
    }

    # Use auth token if available (higher rate limits)
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(api_url, headers=headers, timeout=30)

    if resp.status_code == 404:
        raise ValueError(
            f"PR not found: {url}\n"
            "Check the URL or set GITHUB_TOKEN for private repos."
        )
    if resp.status_code == 403:
        rate_remaining = resp.headers.get("X-RateLimit-Remaining", "")
        if rate_remaining == "0":
            raise ValueError(
                "GitHub API rate limit exceeded. Set GITHUB_TOKEN for higher limits."
            )
        raise ValueError(
            f"GitHub API access forbidden (403). The repo may be private — set GITHUB_TOKEN."
        )
    resp.raise_for_status()

    data = resp.json()
    return {
        "title": data.get("title", "Unknown"),
        "number": data.get("number", parts["number"]),
        "author": data.get("user", {}).get("login", "Unknown"),
        "repo": f"{parts['owner']}/{parts['repo']}",
        "body": data.get("body", "") or "",
        "state": data.get("state", "open"),
        "base_branch": data.get("base", {}).get("ref", "main"),
        "head_branch": data.get("head", {}).get("ref", "unknown"),
        "additions": data.get("additions", 0),
        "deletions": data.get("deletions", 0),
        "changed_files": data.get("changed_files", 0),
        "url": url,
    }


def fetch_pr_diff(url: str) -> str:
    """Fetch the raw diff of a PR."""
    parts = parse_pr_url(url)
    api_url = (
        f"https://api.github.com/repos/{parts['owner']}/{parts['repo']}"
        f"/pulls/{parts['number']}"
    )

    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "GitCourt/1.0",
    }

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(api_url, headers=headers, timeout=60)

    if resp.status_code == 404:
        raise ValueError(
            f"PR not found: {url}\n"
            "Check the URL or set GITHUB_TOKEN for private repos."
        )
    if resp.status_code == 403:
        rate_remaining = resp.headers.get("X-RateLimit-Remaining", "")
        if rate_remaining == "0":
            raise ValueError(
                "GitHub API rate limit exceeded. Set GITHUB_TOKEN for higher limits."
            )
        raise ValueError(
            f"GitHub API access forbidden (403). The repo may be private — set GITHUB_TOKEN."
        )
    resp.raise_for_status()

    return resp.text
