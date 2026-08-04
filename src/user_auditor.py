"""Salesforce User Management & License Hygiene Auditor.

Audits user exports to identify orphaned licenses, dormant administrators,
and over-privileged security permissions.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any


class UserAuditor:
    """Audits Salesforce user records for license optimization and security compliance."""

    def __init__(self, reference_date: str = "2026-10-01T00:00:00Z"):
        self.ref_date = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))

    def audit_users(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        findings = []
        dormant_admins = []
        inactive_with_license = []
        users_without_role = []
        overprivileged_users = []

        total_users = len(users)
        active_count = 0

        for u in users:
            is_active = str(u.get("IsActive", "true")).lower() in ("true", "1", "yes")
            if is_active:
                active_count += 1

            profile = u.get("ProfileName", "")
            last_login = u.get("LastLoginDate", "")
            username = u.get("Username", "Unknown")
            user_id = u.get("Id", "")
            license_type = u.get("LicenseType", "Salesforce")

            # Check 1: Inactive users with paid licenses assigned
            if not is_active and license_type.lower() in ("salesforce", "salesforce platform", "service cloud"):
                inactive_with_license.append({
                    "id": user_id,
                    "username": username,
                    "license": license_type,
                    "reason": "Inactive user still marked with active license assignment."
                })

            # Check 2: Dormant Administrator Accounts (> 90 days since last login)
            if is_active and "administrator" in profile.lower():
                days_inactive = self._calculate_days_inactive(last_login)
                if days_inactive > 90:
                    dormant_admins.append({
                        "id": user_id,
                        "username": username,
                        "days_inactive": days_inactive,
                        "last_login": last_login
                    })

            # Check 3: Active users without a Role in private OWD org
            role_id = u.get("UserRoleId", "")
            if is_active and not role_id and "system administrator" not in profile.lower():
                users_without_role.append({
                    "id": user_id,
                    "username": username,
                    "profile": profile
                })

            # Check 4: Non-admin users with 'Modify All Data' flag
            has_modify_all = str(u.get("PermissionsModifyAllData", "false")).lower() in ("true", "1")
            if is_active and has_modify_all and "system administrator" not in profile.lower():
                overprivileged_users.append({
                    "id": user_id,
                    "username": username,
                    "profile": profile,
                    "risk": "Standard user assigned high-risk Modify All Data permission."
                })

        # Compile actionable recommendations
        if inactive_with_license:
            findings.append({
                "severity": "MEDIUM",
                "category": "License Optimization",
                "summary": f"{len(inactive_with_license)} inactive users are consuming active {license_type} licenses.",
                "remediation": "Reassign license or deactivate user to recover paid licenses."
            })

        if dormant_admins:
            findings.append({
                "severity": "HIGH",
                "category": "Security & Access",
                "summary": f"{len(dormant_admins)} System Administrator accounts have not logged in for over 90 days.",
                "remediation": "Downgrade dormant admin accounts to standard profiles or freeze credentials to mitigate account takeover risks."
            })

        if users_without_role:
            findings.append({
                "severity": "LOW",
                "category": "Data Sharing & Hierarchy",
                "summary": f"{len(users_without_role)} active users have no Role assigned in the role hierarchy.",
                "remediation": "Assign roles to prevent record ownership and reporting visibility blind spots."
            })

        if overprivileged_users:
            findings.append({
                "severity": "HIGH",
                "category": "Profile Governance",
                "summary": f"{len(overprivileged_users)} non-admin users have global 'Modify All Data' rights.",
                "remediation": "Audit and remove 'Modify All Data' from non-system-admin profiles; grant granular object permissions via Permission Sets."
            })

        return {
            "total_users": total_users,
            "active_users": active_count,
            "inactive_users": total_users - active_count,
            "findings": findings,
            "dormant_admins": dormant_admins,
            "inactive_licensed_users": inactive_with_license,
            "users_without_role": users_without_role,
            "overprivileged_users": overprivileged_users
        }

    def _calculate_days_inactive(self, last_login_str: str) -> int:
        if not last_login_str:
            return 999  # Never logged in
        try:
            clean_str = last_login_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            return (self.ref_date - dt).days
        except Exception:
            return 0
