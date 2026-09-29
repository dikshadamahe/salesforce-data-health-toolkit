import unittest
from src.report_health import ReportHealthScanner


class TestReportHealth(unittest.TestCase):
    def setUp(self):
        self.scanner = ReportHealthScanner()

    def test_unindexed_filter_penalty(self):
        reports = [
            {
                "Id": "00O5g000001XXXX",
                "Name": "Open Pipeline by Custom Status",
                "DateFilterScope": "Current FQ",
                "EstimatedRowCount": 5000,
                "Filters": [
                    {"column": "Custom_Status__c", "isIndexed": False}
                ],
                "DaysSinceLastRun": 5
            }
        ]
        result = self.scanner.analyze_reports(reports)
        self.assertLess(result["overall_health_score"], 100)
        self.assertEqual(len(result["unindexed_filter_warnings"]), 1)
        self.assertIn("Custom_Status__c", result["unindexed_filter_warnings"][0]["unindexed_columns"])


if __name__ == "__main__":
    unittest.main()
