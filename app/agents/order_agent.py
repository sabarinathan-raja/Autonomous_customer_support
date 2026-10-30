
from app.schemas import OrderInvestigation
from app.tools.mock_order_api import get_order


def run_order_investigation(
    order_id: str,
) -> OrderInvestigation | None:
    """
    Retrieve and investigate an order using the mock order API.
    """

    order = get_order(order_id)

    if order is None:
        return None

    return order
