from __future__ import annotations

import re

# Conservative checks designed to prevent obvious personal records being sent
# to an external model. They are not a substitute for institutional DLP tools.
_PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "student number": re.compile(r"\b(?:student\s*(?:id|number|no\.?)[\s:#-]*)?\d{8}\b", re.I),
    "UK phone number": re.compile(r"(?<!\d)(?:\+44\s?7\d{3}|07\d{3})[\s-]?\d{3}[\s-]?\d{3}(?!\d)"),
}


def find_sensitive_data(text: str) -> list[str]:
    return [label for label, pattern in _PATTERNS.items() if pattern.search(text)]
