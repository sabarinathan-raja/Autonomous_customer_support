
from app.schemas import (
    IntakeResult,
    OrderInvestigation,
    PolicyEvidence,
    ResolutionResult,
)
from app.tools.gemini_client import generate_customer_response


def run_resolution_agent(
    customer_message: str,
    intake: IntakeResult,
    order: OrderInvestigation | None,
    policies: list[PolicyEvidence],
) -> ResolutionResult:
    """Draft a customer response using verified facts, policies, and Gemini."""

    supporting_evidence = [policy.policy_id for policy in policies]

    # 1. Do not generate a resolution without policy evidence.
    if not policies:
        return ResolutionResult(
            proposed_response=(
                "Thank you for contacting us. We need to review the "
                "applicable support policy before providing a resolution."
            ),
            supporting_evidence=[],
            requires_human_review=True,
        )

    # 2. Ask for the order ID if a required order could not be found.
    if intake.intent in ["delivery", "refund", "cancellation"] and order is None:
        return ResolutionResult(
            proposed_response=(
                "Thank you for contacting us. Please provide a valid "
                "order ID so we can investigate your request."
            ),
            supporting_evidence=supporting_evidence,
            requires_human_review=False,
        )

    # 3. Prepare verified order facts. Do not invent missing information.
    if order is not None:
        order_facts = (
            f"Order ID: {order.order_id}\n"
            f"Order status: {order.status}\n"
            f"Tracking status: {order.tracking_status}\n"
            f"Delivered: {order.delivered}\n"
            f"Promised delivery date: {order.promised_delivery or 'Not available'}"
        )
    else:
        order_facts = "No verified order facts are available."

    # 4. Pass only the retrieved policy evidence to Gemini.
    policy_evidence = "\n".join(
        f"{policy.policy_id}: {policy.content}"
        for policy in policies
    )

    # 5. Draft a response with Gemini.
    try:
        gemini_response = generate_customer_response(
            customer_message=customer_message,
            order_facts=order_facts,
            policy_evidence=policy_evidence,
        )
    except Exception:
        # Safe fallback if Gemini is temporarily unavailable.
        gemini_response = None

    # 6. Keep a deterministic fallback for reliability.
    if not gemini_response:
        if intake.intent == "delivery" and order is not None:
            if order.delivered:
                fallback_response = (
                    f"Our records show that order {order.order_id} has "
                    "been marked as delivered. If you have not received it, "
                    "please let us know so we can investigate."
                )
            else:
                fallback_response = (
                    f"Our records show that order {order.order_id} is "
                    f"currently {order.status}, with tracking status "
                    f"{order.tracking_status}. We understand the inconvenience. "
                    "The available records do not confirm a new delivery date, "
                    "so further checking may be needed."
                )
        elif intake.intent == "refund":
            fallback_response = (
                "Thank you for your refund request. We need to check the "
                "applicable refund conditions before confirming eligibility. "
                "No refund has been approved by this system."
            )
        elif intake.intent == "cancellation":
            fallback_response = (
                "Thank you for your cancellation request. We need to check "
                "your order status and the applicable cancellation conditions. "
                "Your order has not been cancelled by this system."
            )
        else:
            fallback_response = (
                "Thank you for contacting customer support. We will review "
                "your request and determine the next steps."
            )

        gemini_response = fallback_response

    # 7. Require human review for sensitive or unresolved requests.
    requires_human_review = (
        intake.intent in ["refund", "cancellation", "other"]
        or (
            intake.intent == "delivery"
            and order is not None
            and not order.delivered
        )
    )

    return ResolutionResult(
        proposed_response=gemini_response,
        supporting_evidence=supporting_evidence,
        requires_human_review=requires_human_review,
    )
