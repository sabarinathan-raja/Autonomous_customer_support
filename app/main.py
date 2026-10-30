
import re
import csv
from io import StringIO

import streamlit as st

from app.schemas import SupportRequest
from app.workflow.orchestrator import process_support_request
from app.tools.ticket_database import get_ticket_history, get_ticket
from app.tools.ticket_database import delete_all_tickets

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Autonomous Customer Support | Customer Operations",
    page_icon="◈",


    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --bg: #080d18;
        --panel: #101827;
        --panel2: #141f32;
        --border: #25334a;
        --text: #f0f5ff;
        --muted: #91a0b8;
        --blue: #4f8cff;
        --cyan: #56e0df;
        --green: #50d6a0;
        --amber: #ffc66d;
        --red: #ff788b;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(8,13,24,0.92);
    }

    [data-testid="stSidebar"] {
        background: #0c1423;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: #dce7f9;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.5px;
    }

    p, label, .stMarkdown {
        color: #d6dfef;
    }

    .brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #ffffff;
    }

    .brand-mark {
        color: var(--cyan);
    }

    .eyebrow {
        color: var(--cyan);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero {
        background:
            radial-gradient(circle at 85% 15%, rgba(79,140,255,.20), transparent 34%),
            linear-gradient(125deg, #131f35, #101827 60%, #11263a);
        border: 1px solid #2b4263;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(26px, 3vw, 39px);
        line-height: 1.2;
        font-weight: 700;
        color: white;
        margin-bottom: 12px;
    }

    .hero-copy {
        color: #aebed5;
        max-width: 760px;
        font-size: 14px;
        line-height: 1.8;
    }

    .hero-tag {
        display: inline-block;
        color: var(--cyan);
        background: rgba(86,224,223,.09);
        border: 1px solid rgba(86,224,223,.25);
        padding: 6px 10px;
        border-radius: 7px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 18px;
    }

    .panel {
        background: linear-gradient(145deg, #121d2f, #0f1726);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .panel-label {
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 10px;
    }

    .panel-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 27px;
        font-weight: 700;
        color: white;
    }

    .panel-note {
        color: #8497b3;
        font-size: 11px;
        margin-top: 8px;
    }

    .section-kicker {
        color: var(--cyan);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 10px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .section-heading {
        font-family: 'Space Grotesk', sans-serif;
        color: white;
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 14px;
    }

    .agent-card {
        background: #101b2b;
        border: 1px solid #283951;
        border-radius: 12px;
        padding: 15px 12px;
        min-height: 115px;
    }

    .agent-number {
        color: var(--cyan);
        font-size: 10px;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .agent-name {
        color: #f3f7ff;
        font-weight: 700;
        margin-top: 9px;
        font-size: 13px;
    }

    .agent-desc {
        color: #94a5be;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 5px;
    }

    .status-chip {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 6px;
        background: #17283a;
        color: var(--cyan);
        font-size: 11px;
        font-weight: 600;
        border: 1px solid #29445a;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #121d2f, #0e1726);
        border: 1px solid var(--border);
        padding: 17px 18px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9aabc3;
    }

    div[data-testid="stMetricValue"] {
        color: white;
        font-family: 'Space Grotesk', sans-serif;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid #344865;
        transition: border-color .2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--cyan);
        color: white;
    }

    div[data-testid="stForm"] {
        background: #101827;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 22px;
    }

    input, textarea {
        background-color: #0c1422 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #101827;
        border-color: #344865;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        background: #101827;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    hr {
        border-color: var(--border);
    }

    .footer {
        text-align: center;
        color: #6f819c;
        font-size: 11px;
        padding: 20px 0 5px;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 20px;
        }
        .panel-value {
            font-size: 22px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def normalize_order_id(value: str) -> str | None:
    if not value or not value.strip():
        return None

    match = re.search(r"\bORD-\d+\b", value.upper())
    return match.group(0) if match else None


def status_label(status: str) -> str:
    return {
        "answered": "Answered",
        "needs_information": "Needs Information",
        "escalated": "Human Review",
        "failed": "Failed",
    }.get(status, status.replace("_", " ").title())


def status_icon(status: str) -> str:
    return {
        "answered": "✓",
        "needs_information": "!",
        "escalated": "↗",
        "failed": "×",
    }.get(status, "•")


def load_tickets() -> list[dict]:
    try:
        return get_ticket_history(limit=100)
    except Exception as exc:
        st.error("Unable to load ticket records.")
        print(f"Ticket history error: {exc}")
        return []


def make_csv(tickets: list[dict]) -> str:
    output = StringIO()
    fields = [
        "ticket_id",
        "created_at",
        "status",
        "customer_message",
        "order_id",
        "response",
        "escalation_reason",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fields,
        extrasaction="ignore",
    )
    writer.writeheader()

    for ticket in tickets:
        writer.writerow({
            field: ticket.get(field, "")
            for field in fields
        })

    return output.getvalue()


def category_for(message: str) -> str:
    text = message.lower()

    if any(word in text for word in ["refund", "money back", "reimbursement"]):
        return "Refund"

    if any(word in text for word in ["cancel", "cancellation"]):
        return "Cancellation"

    if any(word in text for word in [
        "delivery", "delayed", "late", "tracking",
        "shipping", "where is my order", "not received",
    ]):
        return "Delivery"

    return "Other"


def section_title(kicker: str, title: str):
    st.markdown(
        f'<div class="section-kicker">{kicker}</div>'
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">◈</span> Autonomous Customer Support</div>',
        unsafe_allow_html=True,
    )
    st.caption("AI-POWERED SUPPORT PLATFORM")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Overview",
            "AI Support Desk",
            "Ticket Operations",
            "Human Review Queue",
            "Find a Ticket",
            "Agent Architecture",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("**PLATFORM STATUS**")
    st.markdown(
        '<span class="status-chip">● Application Available</span>',
        unsafe_allow_html=True,
    )

    st.caption("Gemini integration is configured separately.")
    st.caption("Sample order data · SQLite ticket storage")

    st.divider()
    st.caption("Autonomous Customer Support · Development Environment")

    st.divider()

    st.markdown("### Database Management")

    if st.button("🗑️ Clear All Tickets", type="secondary"):
       st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete", False):
       st.warning("Are you sure? All saved tickets will be permanently deleted.")

       col1, col2 = st.columns(2)

       with col1:
           if st.button("Yes, Delete All"):
              delete_all_tickets()
              st.session_state["confirm_delete"] = False
              st.success("All tickets deleted successfully!")
              st.rerun()

       with col2:
           if st.button("Cancel"):
              st.session_state["confirm_delete"] = False
              st.rerun() 

# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">AI OPERATIONS CENTER / CUSTOMER EXPERIENCE</div>
        <div class="hero-title">Customer Intelligence.<br>Autonomous Resolution.</div>
        <div class="hero-copy">
            A policy-aware support platform for customer request intake,
            order investigation, AI-assisted response drafting and
            human escalation — all in one operational workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "DEMO ENVIRONMENT · Uses sample order records and support policies. "
    "This application does not issue real refunds or cancel real orders."
)


# =========================================================
# DATABASE METRICS
# =========================================================

tickets = load_tickets()

total = len(tickets)
answered = sum(t.get("status") == "answered" for t in tickets)
escalated = sum(t.get("status") == "escalated" for t in tickets)
needs_info = sum(t.get("status") == "needs_information" for t in tickets)
failed = sum(t.get("status") == "failed" for t in tickets)

# This is the share of saved tickets marked answered, not a claim
# that AI independently resolved them.
answer_rate = (answered / total * 100) if total else 0

# Derive counts from actual messages for the recent tickets returned.
category_counts = {"Delivery": 0, "Refund": 0, "Cancellation": 0, "Other": 0}
for ticket in tickets:
    category_counts[category_for(ticket.get("customer_message", ""))] += 1


# =========================================================
# PAGE: OVERVIEW
# =========================================================

if page == "Overview":
    section_title("EXECUTIVE VIEW", "Operations Overview")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Total Tickets", total)
    m2.metric("Answered Tickets", answered)
    m3.metric("Human Review Queue", escalated)
    m4.metric("Needs Information", needs_info)

    st.caption(
        f"Answered share of recent saved tickets: {answer_rate:.1f}%. "
        "This is a ticket-status metric, not a verified autonomous-resolution rate."
    )

    st.divider()

    left, right = st.columns([1.25, 1])

    with left:
        section_title("SERVICE PERFORMANCE", "Ticket Status Distribution")

        if total:
            st.bar_chart({
                "Tickets": {
                    "Answered": answered,
                    "Human Review": escalated,
                    "Needs Information": needs_info,
                    "Failed": failed,
                }
            })
        else:
            st.info("No tickets are saved yet. Process a request to populate analytics.")

    with right:
        section_title("REQUEST INTELLIGENCE", "Issue Categories")

        if total:
            st.bar_chart({"Tickets": category_counts})
        else:
            st.info("Category analytics will appear after the first request.")

    st.divider()
    section_title("LATEST ACTIVITY", "Recent Support Requests")

    if not tickets:
        st.info("No activity yet.")
    else:
        for ticket in tickets[:5]:
            status = ticket.get("status", "unknown")

            with st.container(border=True):
                a, b, c = st.columns([2.4, 1, 1])

                with a:
                    st.markdown(f"**{ticket.get('ticket_id', 'Unknown')}**")
                    st.write(ticket.get("customer_message", ""))

                with b:
                    st.caption("STATUS")
                    st.write(f"{status_icon(status)} {status_label(status)}")

                with c:
                    st.caption("ORDER")
                    st.write(ticket.get("order_id") or "Not provided")


# =========================================================
# PAGE: AI SUPPORT DESK
# =========================================================

elif page == "AI Support Desk":
    section_title("CUSTOMER EXPERIENCE", "AI Support Desk")

    st.write(
        "Submit a customer message. The workflow will identify intent, "
        "retrieve policy evidence, investigate available order data, "
        "draft a response and evaluate escalation requirements."
    )

    with st.form("nexus_support_form", clear_on_submit=False):
        customer_message = st.text_area(
            "Customer message",
            placeholder="My delivery is delayed. Can you check order ORD-1042?",
            height=140,
        )

        order_id = st.text_input(
            "Order ID",
            placeholder="ORD-1042",
            help="Optional for requests that do not require an order.",
        )

        submitted = st.form_submit_button(
            "Run Support Workflow  →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not customer_message.strip():
            st.warning("Enter a customer message before submitting.")
        else:
            clean_order_id = (
                normalize_order_id(order_id)
                or normalize_order_id(customer_message)
            )

            try:
                request = SupportRequest(
                    customer_message=customer_message.strip(),
                    order_id=clean_order_id,
                )

                with st.spinner("Processing the support workflow..."):
                    result = process_support_request(request)

                st.session_state["latest_ticket_id"] = result.ticket_id
                
                st.session_state["latest_execution_trace"] = [
                    step.model_dump()
                    for step in result.execution_trace
                ]

                st.divider()
                section_title("WORKFLOW RESULT", "Request Processed")

                r1, r2 = st.columns(2)

                with r1:
                    st.caption("TICKET REFERENCE")
                    st.code(result.ticket_id)

                with r2:
                    st.caption("FINAL STATUS")
                    st.markdown(
                        f"### {status_icon(result.status)} "
                        f"{status_label(result.status)}"
                    )

                st.markdown("#### Customer Response")
                st.markdown(
                    '<div class="panel">',
                    unsafe_allow_html=True,
                )
                st.write(result.response)
                st.markdown("</div>", unsafe_allow_html=True)

                if result.escalation_reason:
                    st.warning(
                        f"Human review reason: {result.escalation_reason}"
                    )
                
                st.divider()
                st.markdown("### Agent Execution Trace")
                st.caption(
                    "Recorded execution details for this request."
                )

                for index, step in enumerate(
                    result.execution_trace, start=1
                ):
                    icon = {
                        "completed": "✅",
                        "failed": "❌",
                        "skipped": "⏭️",
                    }.get(step.status, "•")

                    with st.expander(
                        f"{icon} {index:02d}. {step.agent_name} "
                        f"— {step.duration_ms:.2f} ms"
                    ):
                        st.write("**Status:**", step.status.title())
                        st.write("**Details:**", step.details)

                st.success("Ticket saved. Open Ticket Operations to review it.")

            except Exception as exc:
                st.error(
                    "Unable to process the request. "
                    "Check the VS Code terminal for details."
                )
                print(f"Support request error: {exc}")


# =========================================================
# PAGE: TICKET OPERATIONS
# =========================================================

elif page == "Ticket Operations":
    section_title("SERVICE OPERATIONS", "Ticket Management")

    current_tickets = load_tickets()

    f1, f2 = st.columns([1, 2])

    with f1:
        selected_status = st.selectbox(
            "Filter by status",
            [
                "All",
                "answered",
                "escalated",
                "needs_information",
                "failed",
            ],
        )

    with f2:
        query = st.text_input(
            "Search tickets",
            placeholder="Ticket ID, order ID, or customer message",
        )

    filtered = []

    for ticket in current_tickets:
        if selected_status != "All" and ticket.get("status") != selected_status:
            continue

        searchable = " ".join([
            str(ticket.get("ticket_id", "")),
            str(ticket.get("order_id", "")),
            str(ticket.get("customer_message", "")),
        ]).lower()

        if query.strip().lower() not in searchable:
            continue

        filtered.append(ticket)

    st.caption(f"{len(filtered)} matching tickets · {len(current_tickets)} recent tickets loaded")

    st.download_button(
        "↓ Export filtered tickets as CSV",
        data=make_csv(filtered),
        file_name="customer_support_tickets.csv",
        mime="text/csv",
        use_container_width=False,
    )

    if not filtered:
        st.info("No tickets match the current filters.")
    else:
        for ticket in filtered:
            status = ticket.get("status", "unknown")

            with st.expander(
                f"{status_icon(status)}  {ticket.get('ticket_id', '')}  ·  "
                f"{status_label(status)}  ·  "
                f"{ticket.get('created_at', '')}"
            ):
                c1, c2 = st.columns(2)

                with c1:
                    st.caption("CUSTOMER MESSAGE")
                    st.write(ticket.get("customer_message", ""))
                    st.caption("ORDER ID")
                    st.write(ticket.get("order_id") or "Not provided")

                with c2:
                    st.caption("RESPONSE")
                    st.write(ticket.get("response", ""))
                    st.caption("ESCALATION REASON")
                    st.write(ticket.get("escalation_reason") or "None recorded")


# =========================================================
# PAGE: HUMAN REVIEW QUEUE
# =========================================================

elif page == "Human Review Queue":
    section_title("HUMAN OVERSIGHT", "Human Review Queue")

    queue = [
        ticket for ticket in load_tickets()
        if ticket.get("status") == "escalated"
    ]

    q1, q2 = st.columns(2)
    q1.metric("Pending Human Review", len(queue))
    q2.metric(
        "Recent Tickets Loaded",
        len(tickets),
    )

    st.caption(
        "This page lists escalated tickets for review. "
        "It does not yet record reviewer approvals or rejections."
    )

    if not queue:
        st.success("No escalated tickets in the recent ticket list.")
    else:
        for ticket in queue:
            with st.expander(
                f"↗ {ticket.get('ticket_id', '')} · "
                f"Order {ticket.get('order_id') or 'Not provided'}"
            ):
                st.markdown("**Customer message**")
                st.write(ticket.get("customer_message", ""))

                st.markdown("**Proposed response**")
                st.write(ticket.get("response", ""))

                st.markdown("**Reason for escalation**")
                st.warning(ticket.get("escalation_reason") or "Reason not recorded")


# =========================================================
# PAGE: FIND TICKET
# =========================================================

elif page == "Find a Ticket":
    section_title("RECORD LOOKUP", "Find a Ticket")

    with st.form("nexus_ticket_search"):
        ticket_id = st.text_input(
            "Ticket ID",
            placeholder="TKT-1234ABCD",
        )
        find_submitted = st.form_submit_button(
            "Search Ticket  →",
            type="primary",
        )

    if find_submitted:
        if not ticket_id.strip():
            st.warning("Enter a ticket ID.")
        else:
            try:
                ticket = get_ticket(ticket_id.strip().upper())

                if ticket is None:
                    st.warning("Ticket not found.")
                else:
                    status = ticket.get("status", "unknown")

                    st.success("Ticket found")
                    st.markdown(f"## {ticket.get('ticket_id', '')}")
                    st.markdown(
                        f'<span class="status-chip">'
                        f'{status_label(status)}</span>',
                        unsafe_allow_html=True,
                    )

                    a, b = st.columns(2)

                    with a:
                        st.caption("CREATED AT")
                        st.write(ticket.get("created_at", "Unknown"))

                    with b:
                        st.caption("ORDER ID")
                        st.write(ticket.get("order_id") or "Not provided")

                    st.divider()
                    st.markdown("#### Customer Message")
                    st.write(ticket.get("customer_message", ""))

                    st.markdown("#### Customer Response")
                    st.write(ticket.get("response", ""))

                    st.markdown("#### Escalation Details")
                    st.write(ticket.get("escalation_reason") or "No escalation reason recorded.")

            except Exception as exc:
                st.error("Unable to retrieve the ticket.")
                print(f"Ticket search error: {exc}")


# =========================================================
# PAGE: AGENT ARCHITECTURE
# =========================================================

elif page == "Agent Architecture":
    section_title("SYSTEM DESIGN", "Multi-Agent Workflow")

    st.write(
        "High-level workflow architecture. This is a system overview, "
        "not a live per-agent execution trace."
    )

    agents = [
        ("01", "Intake Agent", "Detect request intent and extract order ID"),
        ("02", "Policy Agent", "Retrieve relevant support policy evidence"),
        ("03", "Order Agent", "Investigate sample order records"),
        ("04", "Gemini AI", "Draft a customer-friendly response"),
        ("05", "Compliance Agent", "Check policy references and risky claims"),
        ("06", "Escalation Agent", "Determine whether human review is required"),
        ("07", "Ticket Database", "Persist the ticket and final response"),
    ]

    for start in range(0, len(agents), 2):
        pair = agents[start:start + 2]
        cols = st.columns(len(pair))

        for col, (number, name, description) in zip(cols, pair):
            with col:
                st.markdown(
                    f"""
                    <div class="agent-card">
                        <div class="agent-number">WORKFLOW STAGE {number}</div>
                        <div class="agent-name">{name}</div>
                        <div class="agent-desc">{description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if start + 2 < len(agents):
            st.markdown(
                '<div style="color:#56e0df;text-align:center;'
                'padding:9px;font-size:18px;">↓</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    st.markdown("#### Operational Guardrails")

    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("**Policy-aware responses**")
        st.caption("Uses retrieved policy evidence to support the response.")

    with g2:
        st.markdown("**Human oversight**")
        st.caption("Escalates requests that need further investigation.")

    with g3:
        st.markdown("**Persistent tickets**")
        st.caption("Stores ticket records in the existing database.")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        ◈ Autonomous Customer Support · ENTERPRISE CUSTOMER OPERATIONS<br>
        AI-assisted support · Policy validation · Human oversight<br><br>
        Prototype environment · Sample order data
    </div>
    """,
    unsafe_allow_html=True,
)
