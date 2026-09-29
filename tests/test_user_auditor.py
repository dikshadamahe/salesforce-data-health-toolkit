import unittest
from src.user_auditor import UserAuditor


class TestUserAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = UserAuditor(reference_date="2026-10-01T00:00:00Z")

    def test_inactive_user_with_license(self):
        users = [
            {
                "Id": "0055g000001AAAA",
                "Username": "jdoe@acme.com",
                "IsActive": "false",
                "LicenseType": "Salesforce",
                "ProfileName": "Standard User"
            }
        ]
        result = self.auditor.audit_users(users)
        self.assertEqual(len(result["inactive_licensed_users"]), 1)
        self.assertEqual(result["findings"][0]["severity"], "MEDIUM")

    def test_dormant_admin_detection(self):
        users = [
            {
                "Id": "0055g000001BBBB",
                "Username": "admin_old@acme.com",
                "IsActive": "true",
                "ProfileName": "System Administrator",
                "LastLoginDate": "2026-05-01T10:00:00Z"
            }
        ]
        result = self.auditor.audit_users(users)
        self.assertEqual(len(result["dormant_admins"]), 1)
        self.assertGreater(result["dormant_admins"][0]["days_inactive"], 90)


if __name__ == "__main__":
    unittest.main()
