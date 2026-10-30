
from time import perf_counter
from uuid import uuid4

from app.schemas import (
    AgentExecutionStep,
    SupportRequest,
    SupportResponse,
)

from app.agents.intake_agent import process_intake
from app.agents.policy_agent import run_policy_agent
from app.agents.order_agent import run_order_investigation
from app.agents.resolution_agent import run_resolution_agent
from app.agents.compliance_agent import run_compliance_agent
from app.agents.escalation_agent import run_escalation_agent

from app.tools.ticket_database import save_ticket


def process_support_request(
    request: SupportRequest,
) -> SupportResponse:
    """Run support agents and record their execution trace."""

    ticket_id = f"TKT-{uuid4().hex[:8].upper()}"
    trace: list[AgentExecutionStep] = []

    def record_step(name: str, details: str, start: float) -> None:
        trace.append(
            AgentExecutionStep(
                agent_name=name,
                status="completed",
                details=details,
                duration_ms=round(
                    (perf_counter() - start) * 1000, 2
                ),
            )
        )

    # 1. Intake Agent
    start = perf_counter()
    intake = process_intake(request)
    record_step(
        "Intake Agent",
        (
            f"Intent: {intake.intent}; "
            f"Order ID: {intake.order_id or 'Not provided'}; "
            f"Priority: {intake.priority}"
        ),
        start,
    )

    # 2. Policy Agent
    start = perf_counter()
    policies = run_policy_agent(request.customer_message)
    policy_ids = [policy.policy_id for policy in policies]
    record_step(
        "Policy Agent",
        (
            f"Retrieved policies: {', '.join(policy_ids)}"
            if policy_ids
            else "No matching policy evidence found."
        ),
        start,
    )

    # 3. Order Agent
    order = None

    if intake.order_id:
        start = perf_counter()
        order = run_order_investigation(intake.order_id)

        if order is None:
            order_details = (
                f"No order record found for {intake.order_id}."
            )
        else:
            order_details = (
                f"Order {order.order_id}: status={order.status}, "
                f"tracking={order.tracking_status}, "
                f"delivered={order.delivered}."
            )

        record_step("Order Agent", order_details, start)
    else:
        trace.append(
            AgentExecutionStep(
                agent_name="Order Agent",
                status="skipped",
                details="No order ID was available for investigation.",
                duration_ms=0.0,
            )
        )

    # 4. Resolution Agent
    start = perf_counter()
    resolution = run_resolution_agent(
        customer_message=request.customer_message,
        intake=intake,
        order=order,
        policies=policies,
    )
    record_step(
        "Resolution Agent",
        (
            "Drafted a response. "
            f"Human review requested: "
            f"{resolution.requires_human_review}."
        ),
        start,
    )

    # 5. Compliance Agent
    start = perf_counter()
    compliance = run_compliance_agent(
        intake=intake,
        resolution=resolution,
        policies=policies,
    )
    record_step(
        "Compliance Agent",
        (
            f"Approved: {compliance.approved}. "
            f"Checks: {len(compliance.reasons)} finding(s)."
        ),
        start,
    )

    # 6. Escalation Agent
    start = perf_counter()
    escalation = run_escalation_agent(
        intake=intake,
        compliance=compliance,
        resolution=resolution,
    )
    record_step(
        "Escalation Agent",
        (
            f"Human review required: {escalation.required}. "
            f"Reason: {escalation.reason or 'None'}"
        ),
        start,
    )

    # 7. Determine final status
    if intake.missing_information:
        status = "needs_information"
    elif escalation.required or not compliance.approved:
        status = "escalated"
    else:
        status = "answered"

    escalation_reason = (
        escalation.reason if escalation.required else None
    )

    # 8. Save ticket to the existing database
    start = perf_counter()

    save_ticket(
        ticket_id=ticket_id,
        customer_message=request.customer_message,
        order_id=intake.order_id,
        status=status,
        response=resolution.proposed_response,
        escalation_reason=escalation_reason,
    )

    record_step(
        "Ticket Database",
        f"Ticket {ticket_id} saved with status: {status}.",
        start,
    )

    # 9. Return response and execution trace
    return SupportResponse(
        ticket_id=ticket_id,
        status=status,
        response=resolution.proposed_response,
        escalation_reason=escalation_reason,
        execution_trace=trace,
    )
