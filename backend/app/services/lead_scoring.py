
from app.models.lead import Lead


HIGH_BUDGET_HINTS = {"high", "enterprise", "100k", "1cr", "crore", "cr", "million", "1m"}
MEDIUM_BUDGET_HINTS = {"medium", "5k", "8k", "lakh", "lakhs", "lac", "50k"}
VAGUE_BUDGET_HINTS = {"not sure", "flexible", "negotiable", "tbd", "depends", "open", "discuss"}
FAST_TIMELINE_HINTS = {"asap", "immediately", "this month", "2 weeks", "urgent", "right away", "this week"}
MID_TIMELINE_HINTS = {"1 month", "2 months", "3 months", "next quarter", "next month", "next week", "30 days", "60 days", "90 days", "next year", "within a year", "6 months"}


def _normalize_budget(budget: str) -> str:
    """Strip currency symbols, commas, whitespace for matching."""
    import re
    cleaned = budget.lower().replace(",", "").replace("$", "").replace("\u20b9", "").strip()
    # Try to detect large numbers: 50000+ → high
    numbers = re.findall(r"\d+", cleaned)
    if numbers:
        largest = max(int(n) for n in numbers)
        if largest >= 100000:
            return "high"  # 1 lakh+ = high
        if largest >= 10000:
            return "50k"   # 10k-99k = medium
    return cleaned


def _score_budget(budget: str | None) -> int:
    if not budget:
        return 0

    normalized = _normalize_budget(budget)
    if any(token in normalized for token in HIGH_BUDGET_HINTS):
        return 30
    if any(token in normalized for token in MEDIUM_BUDGET_HINTS):
        return 20
    if any(token in normalized for token in VAGUE_BUDGET_HINTS):
        return 15
    return 10


def _score_timeline(timeline: str | None) -> int:
    if not timeline:
        return 0

    normalized = timeline.lower()
    if any(token in normalized for token in FAST_TIMELINE_HINTS):
        return 25
    if any(token in normalized for token in MID_TIMELINE_HINTS):
        return 15
    return 8


def calculate_lead_score(lead: Lead) -> int:
    score = 0

    if lead.name:
        score += 8
    if lead.email:
        score += 12
    if lead.phone:
        score += 10

    score += _score_budget(lead.budget)
    score += _score_timeline(lead.timeline)

    if lead.requirement:
        score += 15 if len(lead.requirement.strip()) > 30 else 8

    return min(score, 100)
