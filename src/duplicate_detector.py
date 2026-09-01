"""Duplicate record detection engine for Salesforce datasets.

Identifies exact and normalized duplicate clusters across Lead, Contact,
and Account datasets prior to bulk upsert operations.
"""

import re
from typing import List, Dict, Any
from collections import defaultdict


def normalize_phone(phone: str) -> str:
    """Removes country codes, spaces, and formatting characters."""
    if not phone:
        return ""
    digits = re.sub(r"\D", "", str(phone))
    return digits[-10:] if len(digits) >= 10 else digits


def normalize_email(email: str) -> str:
    """Lowercases and trims email address."""
    return str(email).strip().lower() if email else ""


class DuplicateDetector:
    """Scans datasets for matching contact/lead records based on configurable match rules."""

    def __init__(self, match_fields: List[str] = None):
        self.match_fields = match_fields or ["Email", "Phone"]

    def find_duplicates(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        email_map = defaultdict(list)
        phone_map = defaultdict(list)
        clusters = []

        for idx, row in enumerate(rows, start=2):
            email = normalize_email(row.get("Email", ""))
            phone = normalize_phone(row.get("Phone", ""))

            if email:
                email_map[email].append((idx, row))
            if phone:
                phone_map[phone].append((idx, row))

        # Identify email-based duplicate clusters
        for email, matched_rows in email_map.items():
            if len(matched_rows) > 1:
                clusters.append({
                    "rule": "Exact Match on Normalized Email",
                    "matched_value": email,
                    "count": len(matched_rows),
                    "rows": [r[0] for r in matched_rows],
                    "records": [r[1] for r in matched_rows]
                })

        # Identify phone-based duplicate clusters (excluding already clustered by email)
        for phone, matched_rows in phone_map.items():
            if len(matched_rows) > 1:
                # check if not already caught in email clusters
                row_ids = [r[0] for r in matched_rows]
                already_clustered = any(set(row_ids) == set(c["rows"]) for c in clusters)
                if not already_clustered:
                    clusters.append({
                        "rule": "Exact Match on Standardized 10-Digit Phone",
                        "matched_value": phone,
                        "count": len(matched_rows),
                        "rows": row_ids,
                        "records": [r[1] for r in matched_rows]
                    })

        total_dup_records = sum(c["count"] for c in clusters)

        return {
            "duplicate_clusters_count": len(clusters),
            "total_duplicate_records": total_dup_records,
            "clusters": clusters
        }
