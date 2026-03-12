
from app.models.lead import Lead


HIGH_BUDGET_HINTS = {"high", "enterprise", "10000", "10k", "20000", "20k", "50000", "50k", "100000", "100k", "1cr", "crore", "cr", "million", "1m"}
MEDIUM_BUDGET_HINTS = {"medium", "5000", "5k", "8000", "8k", "lakh", "lakhs", "lac", "50000"}
FAST_TIMELINE_HINTS = {"asap", "immediately", "this month", "2 weeks", "urgent", "right away", "this week"}
MID_TIMELINE_HINTS = {"1 month", "2 months", "3 months", "next quarter", "next month", "next week", "30 days", "60 days", "90 days"}


def _score_budget(budget: str | None) -> int:
    if not budget:
        return 0

    normalized = budget.lower()
    if any(token in normalized for token in HIGH_BUDGET_HINTS):
        return 30
    if any(token in normalized for token in MEDIUM_BUDGET_HINTS):
        return 20
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
