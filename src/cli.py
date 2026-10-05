"""Command-line interface for Salesforce Data Health & Support Diagnostic Toolkit."""

import csv
import json
import argparse
from typing import List, Dict, Any
from src.user_auditor import UserAuditor
from src.data_validator import DataPreFlightValidator
from src.duplicate_detector import DuplicateDetector
from src.report_health import ReportHealthScanner
from src.report_generator import HealthReportFormatter


def read_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Salesforce Data Health & Support Diagnostic Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Diagnostic command")

    # Command: audit-users
    p_users = subparsers.add_parser("audit-users", help="Audit user records for license leaks and admin security")
    p_users.add_argument("--file", "-f", default="sample_data/users_export.csv", help="User export CSV file")

    # Command: validate-csv
    p_csv = subparsers.add_parser("validate-csv", help="Pre-flight validation on CSV before Data Loader / Bulk API")
    p_csv.add_argument("--file", "-f", default="sample_data/leads_import_dirty.csv", help="Import CSV file")
    p_csv.add_argument("--required", "-r", nargs="*", default=["LastName", "Company"], help="Required columns")

    # Command: check-reports
    p_rep = subparsers.add_parser("check-reports", help="Audit reports and dashboards for performance anti-patterns")
    p_rep.add_argument("--file", "-f", default="sample_data/reports_metadata.json", help="Reports metadata JSON")

    # Command: full-audit
    p_full = subparsers.add_parser("full-audit", help="Run comprehensive audit and output client Markdown report")
    p_full.add_argument("--users", default="sample_data/users_export.csv")
    p_full.add_argument("--csv", default="sample_data/leads_import_dirty.csv")
    p_full.add_argument("--reports", default="sample_data/reports_metadata.json")
    p_full.add_argument("--output", "-o", default="health_audit_report.md", help="Output file")

    args = parser.parse_args()

    if args.command == "audit-users":
        users = read_csv(args.file)
        auditor = UserAuditor()
        res = auditor.audit_users(users)
        print(f"\n[USER AUDIT] Total Users: {res['total_users']}, Active: {res['active_users']}")
        for f in res["findings"]:
            print(f"[{f['severity']}] {f['category']}: {f['summary']}")
            print(f"  Remediation: {f['remediation']}\n")

    elif args.command == "validate-csv":
        rows = read_csv(args.file)
        validator = DataPreFlightValidator(required_columns=args.required)
        dup_detector = DuplicateDetector()
        val_res = validator.validate_dataset(rows)
        dup_res = dup_detector.find_duplicates(rows)

        print(f"\n[DATA LOADER PRE-FLIGHT] Rows: {val_res['total_rows']}, Valid: {val_res['valid_rows']}, Errors: {val_res['error_rows']}")
        print(f"Pass Rate: {val_res['pass_rate_percentage']}%")
        for err in val_res["row_errors"]:
            print(f"Row {err['row_number']}: {', '.join(err['errors'])}")

        print(f"\n[DUPLICATE DETECTION] Duplicate Clusters Found: {dup_res['duplicate_clusters_count']}")
        for c in dup_res["clusters"]:
            print(f"Cluster: {c['rule']} ({c['matched_value']}) across rows {c['rows']}")

    elif args.command == "check-reports":
        reps = read_json(args.file)
        scanner = ReportHealthScanner()
        res = scanner.analyze_reports(reps)
        print(f"\n[REPORTS HEALTH] Analyzed: {res['total_reports_analyzed']}, Score: {res['overall_health_score']}/100")
        for rec in res["recommendations"]:
            print(f"- {rec}")

    elif args.command == "full-audit" or args.command is None:
        users = read_csv(args.users if hasattr(args, "users") else "sample_data/users_export.csv")
        csv_rows = read_csv(args.csv if hasattr(args, "csv") else "sample_data/leads_import_dirty.csv")
        reps = read_json(args.reports if hasattr(args, "reports") else "sample_data/reports_metadata.json")

        u_res = UserAuditor().audit_users(users)
        c_res = DataPreFlightValidator(required_columns=["LastName", "Company"]).validate_dataset(csv_rows)
        r_res = ReportHealthScanner().analyze_reports(reps)

        formatter = HealthReportFormatter()
        md = formatter.format_markdown(u_res, c_res, r_res)
        out_file = args.output if hasattr(args, "output") else "health_audit_report.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"\n[SUCCESS] Generated comprehensive org health report: {out_file}\n")
        print(md)


if __name__ == "__main__":
    main()
