from pydantic import BaseModel


class AnalyticsOut(BaseModel):
    total_leads: int
    qualified_leads: int
    qualification_rate: float
    total_conversations: int
    open_conversations: int
    avg_lead_score: float
