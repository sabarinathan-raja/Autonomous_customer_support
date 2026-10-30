
from typing import Literal

from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    customer_message: str = Field(min_length=1)
    order_id: str | None = None
    customer_id: str | None = None


class IntakeResult(BaseModel):
    intent: Literal["delivery", "refund", "cancellation", "other"]
    order_id: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high"] = "medium"


class PolicyEvidence(BaseModel):
    policy_id: str
    content: str
    source: str


class OrderInvestigation(BaseModel):
    order_id: str
    status: str
    tracking_status: str
    delivered: bool
    promised_delivery: str | None = None


class ResolutionResult(BaseModel):
    proposed_response: str
    supporting_evidence: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class ComplianceResult(BaseModel):
    approved: bool
    reasons: list[str] = Field(default_factory=list)


class EscalationResult(BaseModel):
    required: bool
    reason: str | None = None
    target_team: str | None = None


class AgentExecutionStep(BaseModel):
    agent_name: str
    status: Literal["completed", "failed", "skipped"]
    details: str
    duration_ms: float = 0.0


class SupportResponse(BaseModel):
    ticket_id: str
    status: Literal["answered", "needs_information", "escalated", "failed"]
    response: str
    escalation_reason: str | None = None
    execution_trace: list[AgentExecutionStep] = Field(default_factory=list)
