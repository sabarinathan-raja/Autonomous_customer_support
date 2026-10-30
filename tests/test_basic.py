
import pytest

from app.schemas import SupportRequest
from app.workflow.orchestrator import process_support_request
from app.agents.intake_agent import process_intake
from app.agents.order_agent import run_order_investigation
from app.agents.policy_agent import run_policy_agent
from app.tools.ticket_database import (
    get_ticket,
    get_ticket_history,
)


def test_delivery_intent():
    request = SupportRequest(
        customer_message="My delivery is delayed"
    )
    assert process_intake(request).intent == "delivery"


def test_extract_order_id():
    request = SupportRequest(
        customer_message="Delivery delayed. Order ORD-1042"
    )
    assert process_intake(request).order_id == "ORD-1042"


def test_missing_order_id():
    request = SupportRequest(customer_message="I want a refund")
    result = process_intake(request)

    assert result.intent == "refund"
    assert result.order_id is None
    assert "order_id" in result.missing_information


def test_existing_order():
    result = run_order_investigation("ORD-1042")

    assert result is not None
    assert result.status == "delayed"
    assert result.delivered is False


def test_unknown_order():
    assert run_order_investigation("ORD-9999") is None


def test_delivery_policy():
    policies = run_policy_agent("My delivery is delayed")
    assert "DEL-04" in [p.policy_id for p in policies]


def test_refund_policy():
    policies = run_policy_agent("I want a refund")
    assert "REF-01" in [p.policy_id for p in policies]


def test_complete_delivery_workflow():
    request = SupportRequest(
        customer_message="My delivery is delayed",
        order_id="ORD-1042",
    )
    result = process_support_request(request)

    assert result.ticket_id.startswith("TKT-")
    assert result.status == "escalated"
    assert "ORD-1042" in result.response
    assert result.escalation_reason is not None


def test_missing_order_workflow():
    request = SupportRequest(
        customer_message="I want a refund"
    )
    result = process_support_request(request)

    assert result.status == "needs_information"
    assert "order" in result.response.lower()


def test_completed_ticket_is_saved():
    request = SupportRequest(
        customer_message="My delivery is delayed",
        order_id="ORD-1042",
    )
    result = process_support_request(request)

    saved_ticket = get_ticket(result.ticket_id)

    assert saved_ticket is not None
    assert saved_ticket["status"] == result.status
    assert saved_ticket["order_id"] == "ORD-1042"


def test_ticket_history_returns_list():
    history = get_ticket_history(limit=10)

    assert isinstance(history, list)


def test_invalid_history_limit():
    with pytest.raises(ValueError):
        get_ticket_history(limit=0)
