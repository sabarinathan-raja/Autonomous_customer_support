
from app.schemas import PolicyEvidence
from app.tools.policy_search import search_policies


def run_policy_agent(
    customer_message: str,
) -> list[PolicyEvidence]:
    """
    Find relevant company policies for a customer request.
    """

    policies = search_policies(customer_message)

    return policies
