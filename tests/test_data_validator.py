import unittest
from src.data_validator import DataPreFlightValidator, to_18_char_id, validate_salesforce_id


class TestDataValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DataPreFlightValidator(required_columns=["Email", "LastName"])

    def test_15_to_18_char_checksum(self):
        # Known Salesforce ID: 001300000000001 -> 18 char is 001300000000001AAA
        id_15 = "001300000000001"
        id_18 = to_18_char_id(id_15)
        self.assertEqual(id_18, "001300000000001AAA")

        # Test case-safe checksum validation
        is_valid, err = validate_salesforce_id("001300000000001AAA")
        self.assertTrue(is_valid)

    def test_invalid_18_char_checksum(self):
        is_valid, err = validate_salesforce_id("001300000000001ZZZ")
        self.assertFalse(is_valid)
        self.assertIn("Invalid 18-character checksum", err)

    def test_dataset_validation_errors(self):
        rows = [
            {"LastName": "Smith", "Email": "smith@acme.com", "Id": "001300000000001AAA"},
            {"LastName": "", "Email": "invalid-email", "Id": "bad_id"}
        ]
        result = self.validator.validate_dataset(rows)
        self.assertEqual(result["valid_rows"], 1)
        self.assertEqual(result["error_rows"], 1)
        self.assertIn("Missing required field: 'LastName'", result["row_errors"][0]["errors"])


if __name__ == "__main__":
    unittest.main()
