
import json
from pathlib import Path

from app.schemas import OrderInvestigation


# Locate the project folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Location of our sample order data
ORDERS_FILE = PROJECT_ROOT / "data" / "mock_orders.json"


def get_order(order_id: str) -> OrderInvestigation | None:
    """
    Retrieve a sample order by its order ID.

    Returns:
        OrderInvestigation if the order exists.
        None if the order is not found.
    """

    with ORDERS_FILE.open("r", encoding="utf-8") as file:
        orders = json.load(file)

    order = orders.get(order_id)

    if order is None:
        return None

    return OrderInvestigation(**order)
