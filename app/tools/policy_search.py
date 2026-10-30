
import json
from pathlib import Path

from app.schemas import PolicyEvidence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICIES_FILE = PROJECT_ROOT / "knowledge_base" / "support_policies.json"


def search_policies(query: str) -> list[PolicyEvidence]:
    """Find relevant support policies using intent-aware keyword matching."""

    with POLICIES_FILE.open("r", encoding="utf-8") as file:
        policies = json.load(file)

    text = query.lower().replace("-", " ")
    text = " ".join(text.split())

    # Map common customer phrases to policy categories.
    category_terms = {
        "delivery": [
            "delivery", "deliver", "delayed", "delay", "late",
            "shipping", "shipment", "tracking", "transit",
            "where is my order", "not received", "package",
            "parcel", "arrived",
        ],
        "refund": [
            "refund", "money back", "reimbursement", "repay",
        ],
        "cancellation": [
            "cancel", "cancellation", "stop my order",
        ],
    }

    matched_categories = {
        category
        for category, terms in category_terms.items()
        if any(term in text for term in terms)
    }

    scored_results = []

    for policy in policies:
        category = str(policy.get("category", "")).lower()
        policy_id = str(policy.get("policy_id", "")).lower()
        content = str(policy.get("content", "")).lower()
        keywords = [
            str(keyword).lower()
            for keyword in policy.get("keywords", [])
        ]

        searchable_text = " ".join(
            [category, policy_id, content, *keywords]
        )

        score = 0

        # Strongly prioritize a policy matching the detected intent.
        for matched_category in matched_categories:
            if matched_category in category or matched_category in policy_id:
                score += 5

        # Add points for matching policy keywords and meaningful words.
        for keyword in keywords:
            if keyword and keyword in text:
                score += 3

        query_words = set(text.split())
        searchable_words = set(searchable_text.split())

        score += sum(
            1 for word in query_words
            if len(word) > 2 and word in searchable_words
        )

        if score > 0:
            scored_results.append((score, policy))

    # Return the most relevant policies first.
    scored_results.sort(key=lambda item: item[0], reverse=True)

    return [
        PolicyEvidence(
            policy_id=policy["policy_id"],
            content=policy["content"],
            source=policy["source"],
        )
        for _, policy in scored_results
    ]
