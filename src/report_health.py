"""Salesforce Report & Dashboard Performance Health Scanner.

Scans report metadata definitions to identify performance bottlenecks,
unindexed filter anti-patterns, and orphaned dashboard components.
"""

from typing import List, Dict, Any


class ReportHealthScanner:
    """Diagnoses report definitions for query selectivity and dashboard latency risks."""

    def analyze_reports(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        slow_reports = []
        dormant_reports = []
        all_time_filters = []
        unindexed_filters = []

        total = len(reports)
        penalty_points = 0

        for r in reports:
            report_name = r.get("Name", "Unnamed Report")
            report_id = r.get("Id", "")
            date_filter = r.get("DateFilterScope", "")
            filters = r.get("Filters", [])
            last_run_days = r.get("DaysSinceLastRun", 0)
            row_count = r.get("EstimatedRowCount", 0)

            # Check 1: Non-selective "All Time" date filter on large datasets
            if date_filter.lower() in ("all time", "all_time", "") and row_count > 10000:
                penalty_points += 10
                all_time_filters.append({
                    "id": report_id,
                    "name": report_name,
                    "row_count": row_count,
                    "risk": "Report queries all historical rows without selective date boundaries."
                })

            # Check 2: Filtering on unindexed custom fields
            unindexed_cols = []
            for f in filters:
                col = f.get("column", "")
                is_indexed = f.get("isIndexed", False)
                if col.endswith("__c") and not is_indexed:
                    unindexed_cols.append(col)

            if unindexed_cols:
                penalty_points += 15
                unindexed_filters.append({
                    "id": report_id,
                    "name": report_name,
                    "unindexed_columns": unindexed_cols,
                    "risk": f"Query filters on unindexed custom fields ({', '.join(unindexed_cols)}), causing full table scans."
                })

            # Check 3: Dormant reports (> 180 days since last run)
            if last_run_days > 180:
                dormant_reports.append({
                    "id": report_id,
                    "name": report_name,
                    "days_dormant": last_run_days
                })

        overall_health_score = max(0, 100 - penalty_points)

        recommendations = []
        if all_time_filters:
            recommendations.append(
                "Constrain Date Filters from 'All Time' to specific fiscal periods (e.g., 'Current FQ' or 'Last 90 Days') to enable partition pruning."
            )
        if unindexed_filters:
            recommendations.append(
                "Request custom index creation on high-cardinality filter fields via Salesforce Support or designate fields as External IDs."
            )
        if dormant_reports:
            recommendations.append(
                f"Archive or deprecate {len(dormant_reports)} dormant reports unused for over 180 days to streamline org metadata."
            )

        return {
            "total_reports_analyzed": total,
            "overall_health_score": overall_health_score,
            "all_time_filter_warnings": all_time_filters,
            "unindexed_filter_warnings": unindexed_filters,
            "dormant_reports": dormant_reports,
            "recommendations": recommendations
        }
