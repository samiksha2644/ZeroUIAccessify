"""
Simple NLP / regex-based destination extractor.
Works without any ML model — pure pattern matching against known stop names.
If spaCy is available it will also try NER as a fallback.
"""

import re
from typing import Optional, List

# ---------------------------------------------------------------------------
# Known PMPML stop names (kept in sync with seed data)
# ---------------------------------------------------------------------------
KNOWN_STOPS = [
    "Swargate",
    "Shivajinagar",
    "Deccan Gymkhana",
    "Deccan",
    "Pune Station",
    "Katraj",
    "Hadapsar",
    "Kothrud Depot",
    "Kothrud",
    "Wakad",
    "Hinjewadi",
    "Warje",
]

# Phrases users typically say before a destination
_INTENT_PATTERNS = [
    r"(?:go\s+to|take\s+me\s+to|i\s+want\s+to\s+go\s+to|navigate\s+to|head\s+to)\s+(.+)",
    r"(?:bring\s+me\s+to|get\s+me\s+to|drop\s+me\s+at|i\s+need\s+to\s+reach)\s+(.+)",
    r"(?:how\s+do\s+i\s+get\s+to|route\s+to|directions?\s+to)\s+(.+)",
]


def _clean(text: str) -> str:
    """Lower-case and strip punctuation from edges."""
    return re.sub(r"[^\w\s]", "", text).strip().lower()


def extract_destination(raw_text: str, known_stops: Optional[List[str]] = None) -> Optional[str]:
    """
    Attempt to extract a destination name from the user's spoken text.

    Strategy:
    1. Try regex intent patterns (e.g. "take me to Shivajinagar").
    2. Try direct substring match against known stop names.
    3. (Optional) Try spaCy NER for GPE / LOC entities.

    Returns the matched stop name (title-cased) or None.
    """
    if known_stops is None:
        known_stops = KNOWN_STOPS

    text = raw_text.strip()
    text_lower = text.lower()

    # --- 1. Regex intent extraction ---
    for pattern in _INTENT_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            candidate = match.group(1).strip()
            # Try to resolve candidate against known stops
            for stop in known_stops:
                if stop.lower() in candidate or candidate in stop.lower():
                    return stop
            # Return raw candidate title-cased if no exact match
            return candidate.title()

    # --- 2. Direct known-stop substring match ---
    for stop in known_stops:
        if stop.lower() in text_lower:
            return stop

    # --- 3. spaCy NER fallback (if model is installed) ---
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC", "FAC"):
                return ent.text.title()
    except Exception:
        pass  # spaCy not available — that's fine for the MVP

    # --- 4. Last resort: return the last two words (often the place name) ---
    words = text.split()
    if len(words) >= 2:
        fallback = " ".join(words[-2:]).title()
        for stop in known_stops:
            if stop.lower() in fallback.lower():
                return stop
        return fallback
    elif words:
        return words[-1].title()

    return None


def detect_command(raw_text: str) -> Optional[str]:
    """
    Detect special voice commands: repeat, cancel, where am I.
    Returns the command keyword or None.
    """
    text_lower = raw_text.strip().lower()

    if "repeat" in text_lower:
        return "repeat"
    if "cancel" in text_lower:
        return "cancel"
    if "where am i" in text_lower:
        return "where_am_i"

    return None
