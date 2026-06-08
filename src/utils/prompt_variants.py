"""Generate alternative phrasings of a user question via Claude Haiku."""
import json

import anthropic

_client = None
MODEL = "claude-haiku-4-5-20251001"


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def generate_variants(question: str, n: int = 3) -> list[str]:
    """Return n alternative phrasings of question. Falls back to original on error."""
    resp = _get_client().messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                f"Generate {n} alternative phrasings of this question for a document search system.\n"
                f"Each phrasing should approach the same information need differently "
                f"(e.g. more specific, broader, different terminology).\n"
                f"Return ONLY a JSON array of {n} strings. No explanation, no markdown.\n"
                f"Original: {question}"
            ),
        }],
    )
    try:
        variants = json.loads(resp.content[0].text)
        if isinstance(variants, list) and len(variants) == n:
            return variants
    except Exception:
        pass
    return [question] * n
