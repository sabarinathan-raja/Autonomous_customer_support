
import re

from app.schemas import IntakeResult, SupportRequest


def detect_intent(message: str) -> str:
    """Identify the customer's primary support intent."""

    text = message.lower()

    refund_words = ["refund", "money back", "reimbursement"]
    cancellation_words = ["cancel", "cancellation", "stop my order"]
    delivery_words = [
        "delivery",
        "delayed",
        "late",
        "shipping",
        "tracking",
        "not received",
        "where is my order",
    ]

    if any(word in text for word in refund_words):
        return "refund"

    if any(word in text for word in cancellation_words):
        return "cancellation"

    if any(word in text for word in delivery_words):
        return "delivery"

    return "other"


def extract_order_id(message: str) -> str | None:
    """Extract an order ID such as ORD-1042 from the message."""

    match = re.search(r"\bORD-\d+\b", message.upper())
    return match.group(0) if match else None


def process_intake(request: SupportRequest) -> IntakeResult:
    """Analyze the incoming customer support request."""

    intent = detect_intent(request.customer_message)

    order_id = request.order_id or extract_order_id(
        request.customer_message
    )

    missing_information = []

    if intent in ["delivery", "refund", "cancellation"] and not order_id:
        missing_information.append("order_id")

    priority = "medium"

    urgent_words = [
        "urgent",
        "emergency",
        "safety issue",
        "fraud",
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
