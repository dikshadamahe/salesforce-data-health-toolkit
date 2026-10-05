# Salesforce Data Health & Support Diagnostic Toolkit

An automated CRM data hygiene, user license audit, and reporting performance diagnostic utility engineered for Salesforce Support Engineers and Administrators.

---

## Why I Built This
In frontline Salesforce Cloud Success operations, support engineers frequently encounter issues originating from preventable customer configuration or data anomalies:
1. **User Management Waste & Security Risks:** Inactive or departing users often continue consuming expensive paid Salesforce licenses. Even worse, dormant System Administrator accounts remain active without logins for 90+ days, introducing compliance vulnerabilities.
2. **Data Loader Batch Failures:** Customers frequently submit urgent support cases when bulk imports fail with errors like `FIELD_CUSTOM_VALIDATION_EXCEPTION`, malformed ISO dates, or truncated Salesforce record IDs.
3. **Slow Executive Dashboards:** Reports filtering across hundreds of thousands of records without indexed custom fields or date boundaries cause dashboard timeouts.

This toolkit provides an automated pre-flight and org audit suite that equips support engineers to diagnose issues rapidly, reduce Average Handle Time (AHT), and provide authoritative best-practice advice.

---

## Key Capabilities

- **User Management & License Auditor (`user_auditor.py`):**
  - Scans user exports to uncover inactive users still holding active paid licenses (`Salesforce`, `Service Cloud`, etc.).
  - Detects dormant System Administrator accounts with no login activity for >90 days.
  - Identifies active users with no role assigned in private OWD sharing models.
  - Flags non-admin profiles with dangerous `Modify All Data` permissions.
- **Data Loader Pre-Flight CSV Validator (`data_validator.py`):**
  - Implements the official Salesforce 15-character to 18-character case-safe ID algorithm and verifies checksum integrity.
  - Validates RFC-5322 email patterns, ISO-8601 date formats, and required field columns.
  - Pinpoints exact row numbers and offending columns prior to Bulk API execution.
- **Duplicate Detection Engine (`duplicate_detector.py`):**
  - Scans import datasets for exact and normalized duplicate matches (email normalization and standardized 10-digit phone parsing).
  - Groups duplicate clusters to prevent polluting customer CRM databases.
- **Report & Dashboard Performance Diagnostic (`report_health.py`):**
  - Evaluates report query selectivity, penalizing unindexed custom field filters (`__c`) on large tables.
  - Flags non-selective "All Time" date filters on high-volume objects.
  - Highlights dormant reports (>180 days without execution).
- **Client Guidance Report Generator (`report_generator.py`):**
  - Generates ready-to-share Markdown and JSON audit summaries for customer case emails and internal case documentation.

---

## Project Structure

```
salesforce-data-health-toolkit/
├── sample_data/
│   ├── users_export.csv           # Sample user records with active/inactive licenses
│   ├── leads_import_dirty.csv     # Sample CSV with malformed IDs, emails & duplicates
│   └── reports_metadata.json      # Sample report definitions and performance metrics
├── src/
│   ├── __init__.py
│   ├── user_auditor.py            # User license, dormant admin & profile auditor
│   ├── data_validator.py          # 15/18-char ID checksum & CSV pre-flight validator
│   ├── duplicate_detector.py      # Normalized duplicate cluster detector
│   ├── report_health.py           # Report query selectivity & dashboard diagnostic
│   ├── report_generator.py        # Executive markdown audit report formatter
│   └── cli.py                     # CLI commands for support engineers
├── tests/
│   ├── __init__.py
│   ├── test_user_auditor.py
│   ├── test_data_validator.py
│   └── test_report_health.py
├── requirements.txt
└── README.md
```

---

## Installation & Setup

```bash
git clone https://github.com/dikshadamahe/salesforce-data-health-toolkit.git
cd salesforce-data-health-toolkit
pip install -r requirements.txt
```

### Running Test Suite
```bash
python3 -m unittest discover tests
```

---

## CLI Usage

### 1. Audit Users & Recover Paid Licenses
```bash
python3 -m src.cli audit-users --file sample_data/users_export.csv
```

### 2. Pre-Flight Validate CSV Before Data Loader Import
```bash
python3 -m src.cli validate-csv --file sample_data/leads_import_dirty.csv
```

### 3. Check Report Query Performance
```bash
python3 -m src.cli check-reports --file sample_data/reports_metadata.json
```

### 4. Run Full Org Diagnostic and Generate Markdown Report
```bash
python3 -m src.cli full-audit --output audit_report.md
```

---

## Author
**Diksha Damahe**  
*B.Tech Computer Science & Engineering (AI & ML), VIT Bhopal University*  
[LinkedIn](https://www.linkedin.com/in/dikshadamahe) • [GitHub](https://github.com/dikshadamahe)
