
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_DIR = PROJECT_ROOT / "data"
DATABASE_FILE = DATABASE_DIR / "tickets.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_FILE,
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the ticket table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_message TEXT NOT NULL,
                order_id TEXT,
                status TEXT NOT NULL CHECK (
                    status IN (
                        'answered',
                        'needs_information',
                        'escalated',
                        'failed'
                    )
                ),
                response TEXT NOT NULL,
                escalation_reason TEXT,
                created_at TEXT NOT NULL DEFAULT
                    (strftime('%Y-%m-%d %H:%M:%S', 'now'))
            )
            """
        )


def save_ticket(
    ticket_id: str,
    customer_message: str,
    order_id: str | None,
    status: str,
    response: str,
    escalation_reason: str | None,
):
    """Validate and save a support ticket."""
    if not ticket_id or not ticket_id.strip():
        raise ValueError("Ticket ID cannot be empty.")

    if not customer_message or not customer_message.strip():
        raise ValueError("Customer message cannot be empty.")

    if status not in {
        "answered",
        "needs_information",
        "escalated",
        "failed",
    }:
        raise ValueError(f"Invalid ticket status: {status}")

    initialize_database()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tickets (
                ticket_id,
                customer_message,
                order_id,
                status,
                response,
                escalation_reason
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id.strip(),
                customer_message.strip(),
                order_id,
                status,
                response,
                escalation_reason,
            ),
        )


def get_ticket_history(limit: int = 50) -> list[dict]:
    """Return the most recent tickets."""
    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT ticket_id, customer_message, order_id, status,
                   response, escalation_reason, created_at
            FROM tickets
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_ticket(ticket_id: str) -> dict | None:
    """Find a ticket by its ID."""
    if not ticket_id or not ticket_id.strip():
        return None

    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT ticket_id, customer_message, order_id, status,
                   response, escalation_reason, created_at
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id.strip(),),
        ).fetchone()

    return dict(row) if row else None
def delete_all_tickets():
    """Delete all saved support tickets safely."""

    initialize_database()

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tickets"
        )
        deleted_count = cursor.rowcount
        connection.commit()

    return deleted_count