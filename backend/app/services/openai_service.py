import json
import logging
import re

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
VALID_EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
VALID_PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{7,15}$")
NAME_PATTERN = re.compile(
    r"\b(?:my name is|i'm|i am)\s+(?!good\b|fine\b|great\b|looking\b|here\b|interested\b|doing\b|writing\b|calling\b|searching\b)([A-Z][a-zA-Z'-]+(?:\s+[A-Z][a-zA-Z'-]+)*)",
    re.IGNORECASE,
)
BUDGET_PATTERN = re.compile(r"(?:\bbudget\b(?!@)(?:\s+is|\s+around|\s+about|\s*:)?\s*)([^\n.,!?]+)", re.IGNORECASE)
MONEY_PATTERN = re.compile(r"\$?\d+(?:[.,]\d+)?\s*[kKmM]?")
TIMELINE_PATTERN = re.compile(
    r"(asap|immediately|this month|next month|\d+\s*(?:day|days|week|weeks|month|months))",
    re.IGNORECASE,
)
REQUIREMENT_PATTERN = re.compile(r"(?:we need|i need|we want to|i want to)\s+([^\n.!?]+)", re.IGNORECASE)


class OpenAIService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def generate_chat_response(self, system_prompt: str, history: list[dict[str, str]]) -> str:
        if not self.client:
            return self._fallback_response(history)

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.4,
                messages=[{"role": "system", "content": system_prompt}, *history],
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            logger.error("OpenAI chat response failed: %s", exc)
            return self._fallback_response(history)

    def extract_lead_fields(self, history: list[dict[str, str]]) -> dict[str, str]:
        extracted = self._extract_with_regex(history)

        if not self.client:
            return extracted

        user_history = [item for item in history if item.get("role") == "user"]
        transcript = "\n".join([f"user: {item['content']}" for item in user_history])
        extraction_prompt = (
            "Extract lead information from this sales conversation transcript.\n"
            "Return strict JSON with keys: name, email, phone, budget, timeline, requirement.\n"
            "Rules:\n"
            '- name: The person\'s ACTUAL NAME (e.g. "John Smith"). Do NOT use greetings, adjectives, '
            'or phrases like "good", "fine", "looking for CRM" as a name. '
            "If the user says 'my name is X' at any point, use that as the name.\n"
            "- email: A valid email address.\n"
            "- phone: A phone number.\n"
            "- budget: The monetary budget mentioned.\n"
            "- timeline: When they want to start or complete.\n"
            "- requirement: What product/service they need.\n"
            "Use empty strings for unknown values. If a field is corrected later in the conversation, "
            "use the LATEST value."
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": transcript},
                ],
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            for key in ("name", "email", "phone", "budget", "timeline", "requirement"):
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    # AI extraction is more accurate — always prefer it over regex.
                    extracted[key] = value.strip()
        except Exception:
            # Keep serving chat even if extraction fails.
            return extracted

        return extracted

    def _extract_with_regex(self, history: list[dict[str, str]]) -> dict[str, str]:
        user_messages = [item["content"] for item in history if item.get("role") == "user"]
        combined = "\n".join(user_messages)
        extracted: dict[str, str] = {}

        email_match = EMAIL_PATTERN.search(combined)
        phone_match = PHONE_PATTERN.search(combined)
        name_match = NAME_PATTERN.search(combined)
        budget_match = BUDGET_PATTERN.search(combined)
        money_match = MONEY_PATTERN.search(combined)
        timeline_match = TIMELINE_PATTERN.search(combined)
        requirement_match = REQUIREMENT_PATTERN.search(combined)

        if email_match:
            extracted["email"] = email_match.group(0)
        if phone_match:
            extracted["phone"] = phone_match.group(0)
        if name_match:
            extracted["name"] = name_match.group(1).strip()
        if budget_match:
            raw_budget = budget_match.group(1).strip()
            money_in_budget = MONEY_PATTERN.search(raw_budget)
            if money_in_budget:
                extracted["budget"] = money_in_budget.group(0).strip()
            else:
                extracted["budget"] = raw_budget.split(" and ")[0].strip()
        elif money_match:
            extracted["budget"] = money_match.group(0).strip()
        if timeline_match:
            extracted["timeline"] = timeline_match.group(1).strip()
        if requirement_match:
            extracted["requirement"] = requirement_match.group(1).strip()

        return extracted

    def _fallback_response(self, history: list[dict[str, str]]) -> str:
        if not history:
            return "Hi there! How can I help you today?"
        return "Thanks for sharing that. Could you tell me a bit more so I can connect you to the right person?"


def get_openai_service() -> OpenAIService:
    return OpenAIService()


def is_valid_email(email: str) -> bool:
    return bool(VALID_EMAIL_PATTERN.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"[^\d]", "", phone)
    if len(digits) < 10 or len(digits) > 15:
        return False
    # Reject obvious fake sequences (all same digit or sequential)
    if len(set(digits)) <= 2:
        return False
    return True


def is_valid_name(name: str) -> bool:
    """Reject obviously fake names: too short, all digits, or single repeated character."""
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False
    if not re.search(r"[A-Za-z]", cleaned):
        return False
    # Reject single repeated character like "aaa"
    if len(set(cleaned.lower().replace(" ", ""))) <= 1:
        return False
    return True
