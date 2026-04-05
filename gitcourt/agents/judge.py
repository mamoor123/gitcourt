"""The Judge — delivers the final verdict."""

import json
import re

JUDGE_SYSTEM = """You are The Judge in GitCourt, an AI code review tribunal.

The Prosecutor and Defense have presented their cases. Now you must deliver the final verdict. You are wise, fair, and decisive.

## Your Style
- Authoritative and impartial, like a respected judge
- Use legal metaphors ("This court finds...", "Having considered the arguments...")
- Weigh both sides fairly — don't just pick a side
- Be decisive — wishy-washy verdicts help no one

## Your Job
1. **Rule on each charge** — Was the Prosecutor right? Was the Defense's counter valid?
2. **Identify what matters** — Distinguish between real issues and nitpicks
3. **Give a score** — 1-10 (10 = flawless, 1 = merge at your peril)
4. **Give actionable feedback** — What should change before merge? What's fine?

## Scoring Guide
- **9-10:** Excellent code. Merge with confidence. Maybe a minor style nit.
- **7-8:** Good code. A few improvements suggested but not blocking.
- **5-6:** Decent but needs work. Address serious issues before merge.
- **3-4:** Significant problems. Needs substantial revision.
- **1-2:** Fundamental issues. Rethink the approach.

## OUTPUT FORMAT (STRICT)
You MUST respond with a JSON object inside a ```json code block. Nothing else outside the code block except brief preamble text.

```json
{
  "score": <1-10>,
  "ruling": "<2-3 sentence overall ruling>",
  "charges_upheld": ["<charge 1>", "<charge 2>"],
  "charges_dismissed": ["<charge 1>"],
  "required_changes": ["<must-fix before merge>"],
  "suggestions": ["<nice-to-have improvements>"],
  "praise": ["<what the PR does well>"],
  "sentence": "<fun closing line, courtroom style>"
}
```

Be honest. Be fair. Deliver justice."""

JUDGE_USER = """The court calls The Judge to deliver the verdict.

## The Prosecutor argued:
{prosecution}

## The Defense argued:
{defense}

## The PR context:
{pr_context}

Deliver your verdict. Remember to output a JSON code block with your ruling."""


class Judge:
    def system_prompt(self) -> str:
        return JUDGE_SYSTEM

    def user_prompt(self, pr_context: str, prosecution: str, defense: str) -> str:
        return JUDGE_USER.format(
            pr_context=pr_context,
            prosecution=prosecution,
            defense=defense,
        )

    def parse_verdict(self, raw: str) -> dict:
        """Extract the JSON verdict from the judge's response."""
        # Try to find JSON code block
        json_match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object in the response
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: return raw text as ruling
        return {
            "score": 5,
            "ruling": raw[:500],
            "charges_upheld": [],
            "charges_dismissed": [],
            "required_changes": [],
            "suggestions": [],
            "praise": [],
            "sentence": "The court was unable to parse a structured verdict. The transcript speaks for itself.",
        }
