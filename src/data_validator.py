"""Salesforce Data Loader & Bulk API Pre-Flight CSV Validator.

Validates CSV datasets before upload to prevent upload failures and API governor limit consumption.
Includes 15-character to 18-character case-safe ID checksum calculation.
"""

import re
from typing import List, Dict, Any, Tuple, Optional


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2}))?$")
ID_LOOKUP_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"


def to_18_char_id(id_15: str) -> str:
    """Converts a 15-character case-sensitive Salesforce ID into an 18-character case-safe ID

    using standard Salesforce 3-character checksum algorithm.
    """
    if len(id_15) != 15:
        return id_15

    suffix = ""
    for block_idx in range(3):
        block = id_15[block_idx * 5: (block_idx + 1) * 5]
        bit_val = 0
        for i, char in enumerate(block):
            if char.isupper():
                bit_val |= (1 << i)
        suffix += ID_LOOKUP_CHARS[bit_val]

    return id_15 + suffix


def validate_salesforce_id(sf_id: str) -> Tuple[bool, Optional[str]]:
    """Checks whether a Salesforce ID is valid (15 or 18 alphanumeric characters)

    and verifies 18-char checksum consistency.
    """
    if not sf_id or not isinstance(sf_id, str):
        return False, "Empty or non-string ID"

    sf_id = sf_id.strip()
    if len(sf_id) == 15:
        if sf_id.isalnum():
            return True, None
        return False, "15-character ID contains invalid special characters"

    if len(sf_id) == 18:
        if not sf_id.isalnum():
            return False, "18-character ID contains invalid special characters"
        base_15 = sf_id[:15]
        expected_18 = to_18_char_id(base_15)
        if sf_id.upper() == expected_18.upper():
            return True, None
        return False, f"Invalid 18-character checksum (expected suffix {expected_18[15:]}, found {sf_id[15:]})"

    return False, f"Invalid length ({len(sf_id)} chars; Salesforce IDs must be 15 or 18 chars)"


class DataPreFlightValidator:
    """Performs pre-flight validation on CSV records before Salesforce Data Loader ingestion."""

    def __init__(self, required_columns: List[str] = None, id_columns: List[str] = None):
        self.required_columns = required_columns or []
        self.id_columns = id_columns or ["Id", "AccountId", "ContactId", "OwnerId"]

    def validate_dataset(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        row_errors = []
        valid_rows_count = 0

        for idx, row in enumerate(rows, start=2):  # start at 2 assuming row 1 is header
            errors = []

            # 1. Required column presence
            for col in self.required_columns:
                val = str(row.get(col, "")).strip()
                if not val:
                    errors.append(f"Missing required field: '{col}'")

            # 2. Email format validation
            for col, val in row.items():
                if "email" in col.lower() and val:
                    clean_val = str(val).strip()
                    if not EMAIL_REGEX.match(clean_val):
                        errors.append(f"Malformed email in '{col}': '{clean_val}'")

            # 3. Salesforce ID checksum validation
            for col in self.id_columns:
                if col in row and row[col]:
                    val = str(row[col]).strip()
                    is_valid, err_msg = validate_salesforce_id(val)
                    if not is_valid:
                        errors.append(f"Invalid Salesforce ID in '{col}' ({val}): {err_msg}")

            # 4. Date format validation
            for col, val in row.items():
                if ("date" in col.lower() or "created" in col.lower()) and val:
                    clean_val = str(val).strip()
                    if not DATE_REGEX.match(clean_val):
                        errors.append(f"Invalid date format in '{col}' ('{clean_val}'; expected YYYY-MM-DD or ISO-8601)")

            if errors:
                row_errors.append({
                    "row_number": idx,
                    "errors": errors,
                    "row_data": row
                })
            else:
                valid_rows_count += 1

        return {
            "total_rows": len(rows),
            "valid_rows": valid_rows_count,
            "error_rows": len(row_errors),
            "pass_rate_percentage": round((valid_rows_count / len(rows) * 100), 2) if rows else 0.0,
            "row_errors": row_errors
        }
