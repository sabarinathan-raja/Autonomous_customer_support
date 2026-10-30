
from app.schemas import (
    ComplianceResult,
    EscalationResult,
    IntakeResult,
    ResolutionResult,
)


def run_escalation_agent(
    intake: IntakeResult,
    compliance: ComplianceResult,
    resolution: ResolutionResult,
) -> EscalationResult:
    """Decide whether a support case needs human escalation."""

    # Missing order information needs customer follow-up.
    if intake.missing_information:
        return EscalationResult(
            required=False,
            reason="Required information is missing. Ask the customer for it.",
            target_team=None,
        )

    # High-priority requests should be reviewed by a human.
    if intake.priority == "high":
        return EscalationResult(
            required=True,
            reason="The request has been marked as high priority.",
            target_team="Priority Support Team",
        )

    # Compliance failures require human review.
    if not compliance.approved:
        return EscalationResult(
            required=True,
            reason="Compliance checks did not approve the draft.",
            target_team="Human Review Team",
        )

    # Resolution agent may explicitly request human review.
    if resolution.requires_human_review:
        return EscalationResult(
            required=True,
            reason="The proposed resolution requires human review.",
            target_team="Customer Support Team",
        )

    # No escalation condition was found.
    return EscalationResult(
        required=False,
        reason=None,
        target_team=None,
    )
