"""Terminal formatter — makes GitCourt output look amazing."""

import shutil


# ANSI colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def get_terminal_width() -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def print_banner():
    banner = f"""
{C.CYAN}{C.BOLD}
   ▄████ ▄▄▄█████▓ ██▀███   ▄▄▄       ▄████▄   ██▓ ███▄    █   ▄████
  ██▒ ▀█▒▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    ▒██▀ ▀█  ▓██▒ ██ ▀█   █  ██▒ ▀█▒
 ▒██░▄▄▄░▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▒██▒▓██  ▀█ ██▒▒██░▄▄▄░
 ░▓█  ██▓░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄▄ ▒▓▓▄ ▄██▒░██░▓██▒  ▐▌██▒░▓█  ██▓
 ░▒▓███▀▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░░██░▒██░   ▓██░░▒▓███▀▒
  ░▒   ▒   ░ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒
   ░   ░     ░░     ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒    ▒ ░ ░ ░░   ░ ▒░  ░   ░
{C.RESET}
{C.DIM}  Three AI agents. One Pull Request. Justice will be served.{C.RESET}
"""
    print(banner)


def print_case_header(pr_info: dict):
    w = get_terminal_width()
    print(f"{C.BOLD}{'═' * w}{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}  📋 CASE #{pr_info['number']}: {pr_info['title']}{C.RESET}")
    print(f"{C.DIM}  Repo: {pr_info['repo']} | Author: @{pr_info['author']}{C.RESET}")

    changes = f"+{pr_info.get('additions', '?')} -{pr_info.get('deletions', '?')} ({pr_info.get('changed_files', '?')} files)"
    print(f"{C.DIM}  Changes: {changes}{C.RESET}")

    if pr_info.get("body"):
        body_preview = pr_info["body"][:200].replace("\n", " ")
        if len(pr_info["body"]) > 200:
            body_preview += "..."
        print(f"{C.DIM}  Description: {body_preview}{C.RESET}")

    print(f"{C.BOLD}{'═' * w}{C.RESET}")
    print()


def print_separator():
    w = get_terminal_width()
    print(f"\n{C.DIM}{'─' * w}{C.RESET}\n")


def print_agent_argument(role: str, emoji: str, argument: str):
    # Print role header
    if role == "PROSECUTOR":
        color = C.RED
    elif role == "DEFENDER":
        color = C.BLUE
    else:
        color = C.YELLOW

    print(f"{color}{C.BOLD}  {emoji} {role}{C.RESET}")
    print()

    # Print argument with slight indent
    for line in argument.split("\n"):
        print(f"  {line}")
    print()


def print_score_bar(score: int):
    """Print a visual score bar from 1-10."""
    score = max(1, min(10, int(score)))
    w = 40  # bar width
    filled = int((score / 10) * w)
    empty = w - filled

    # Color based on score
    if score >= 8:
        color = C.GREEN
        label = "APPROVED ✅"
    elif score >= 6:
        color = C.YELLOW
        label = "NEEDS WORK 🔧"
    elif score >= 4:
        color = C.YELLOW
        label = "CHANGES REQUESTED ⚠️"
    else:
        color = C.RED
        label = "REJECTED ❌"

    bar = f"{color}{'█' * filled}{C.DIM}{'░' * empty}{C.RESET}"
    print(f"  {C.BOLD}Score: {score}/10{C.RESET}  [{bar}]  {color}{C.BOLD}{label}{C.RESET}")


def _ensure_list(value):
    """Ensure value is a list (LLM might return a string instead)."""
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        return [value]
    return []


def print_verdict(verdict: dict):
    """Print the judge's verdict in a formatted way."""
    color = C.YELLOW

    print(f"{color}{C.BOLD}  🟡 THE VERDICT{C.RESET}")
    print()

    # Ruling
    if verdict.get("ruling"):
        print(f"  {C.BOLD}\"{verdict['ruling']}\"{C.RESET}")
        print()

    # Charges
    charges_upheld = _ensure_list(verdict.get("charges_upheld"))
    if charges_upheld:
        print(f"  {C.RED}Charges Upheld:{C.RESET}")
        for charge in charges_upheld:
            print(f"    ❌ {charge}")
        print()

    charges_dismissed = _ensure_list(verdict.get("charges_dismissed"))
    if charges_dismissed:
        print(f"  {C.GREEN}Charges Dismissed:{C.RESET}")
        for charge in charges_dismissed:
            print(f"    ✅ {charge}")
        print()

    # Required changes
    required = _ensure_list(verdict.get("required_changes"))
    if required:
        print(f"  {C.YELLOW}Required Before Merge:{C.RESET}")
        for change in required:
            print(f"    🔧 {change}")
        print()

    # Suggestions
    suggestions = _ensure_list(verdict.get("suggestions"))
    if suggestions:
        print(f"  {C.CYAN}Suggestions:{C.RESET}")
        for sug in suggestions:
            print(f"    💡 {sug}")
        print()

    # Praise
    praise = _ensure_list(verdict.get("praise"))
    if praise:
        print(f"  {C.GREEN}Commendations:{C.RESET}")
        for p in praise:
            print(f"    🌟 {p}")
        print()

    # Sentence (fun closing)
    if verdict.get("sentence"):
        print(f"  {C.DIM}{C.MAGENTA}\"{verdict['sentence']}\"{C.RESET}")
