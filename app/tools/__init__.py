import re

from app.schemas import IntakeResult, SupportRequest


def detect_intent(message: str) -> str:
    text = message.lower()

    if any(word in text for word in [
        "refund", "money back", "reimbursement"
    ]):
        return "refund"

    if any(word in text for word in [
        "cancel", "cancellation", "stop my order"
    ]):
        return "cancellation"

    if any(word in text for word in [
        "delivery", "delayed", "late", "shipping",
        "tracking", "not received", "where is my order"
    ]):
        return "delivery"

    return "other"


def extract_order_id(message: str) -> str | None:
    match = re.search(r"\bORD-\d+\b", message.upper())
    return match.group(0) if match else None


def process_intake(request: SupportRequest) -> IntakeResult:
    intent = detect_intent(request.customer_message)

    # Prefer the order ID supplied in the separate field.
    order_id = (
        extract_order_id(request.order_id)
        if request.order_id
        else None
    )

    # If it is not in the separate field, check the message.
    if not order_id:
        order_id = extract_order_id(request.customer_message)

    missing_information = []

    if intent in ["delivery", "refund", "cancellation"]:
        if not order_id:
            missing_information.append("order_id")

    priority = "medium"

    urgent_words = [
        "urgent", "emergency", "safety issue", "fraud"
    ]

    if any(
        word in request.customer_message.lower()
        for word in urgent_words
    ):
        priority = "high"

    return IntakeResult(
        intent=intent,
        order_id=order_id,
        missing_information=missing_information,
        priority=priority,
    )