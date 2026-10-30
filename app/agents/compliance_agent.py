
from app.schemas import (
    ComplianceResult,
    IntakeResult,
    PolicyEvidence,
    ResolutionResult,
)


def run_compliance_agent(
    intake: IntakeResult,
    resolution: ResolutionResult,
    policies: list[PolicyEvidence],
) -> ComplianceResult:
    """Check the draft for policy support and unsafe claims."""

    reasons = []
    response = resolution.proposed_response.lower()
    policy_ids = {policy.policy_id for policy in policies}

    # Policy evidence must be available.
    if not policies:
        reasons.append("No supporting policy evidence was found.")

    # All referenced policy IDs must exist.
    for policy_id in resolution.supporting_evidence:
        if policy_id not in policy_ids:
            reasons.append(
                f"Referenced policy {policy_id} was not found."
            )

    # Refund requests must not claim an unverified approval or payment.
    if intake.intent == "refund":
        risky_refund_phrases = [
            "your refund has been approved",
            "refund has been approved",
            "your refund is approved",
            "your refund has been processed",
            "refund has been issued",
            "money has been returned",
        ]

        if any(phrase in response for phrase in risky_refund_phrases):
            reasons.append(
                "The response may claim an unverified refund approval or payment."
            )

    # Cancellation requests must not claim an unverified cancellation.
    if intake.intent == "cancellation":
        risky_cancellation_phrases = [
            "your order has been cancelled",
            "your cancellation is complete",
            "order cancellation is confirmed",
            "your order is now cancelled",
        ]

        if any(phrase in response for phrase in risky_cancellation_phrases):
            reasons.append(
                "The response may claim an unverified cancellation."
            )

    # Do not confuse a need for human review with a compliance failure.
    # Escalation Agent handles resolution.requires_human_review separately.

    return ComplianceResult(
        approved=len(reasons) == 0,
        reasons=reasons,
    )
