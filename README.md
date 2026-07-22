# Salesforce Data Health & Support Diagnostic Toolkit

A lightweight diagnostic and audit toolkit built for Salesforce Support Engineers and System Administrators to analyze user management hygiene, pre-validate Data Loader / Bulk API imports, and detect reporting performance bottlenecks.

## Motivation
A substantial portion of Salesforce customer support tickets stem from common, preventable configuration and data discrepancies:
- Users consuming paid licenses while inactive or dormant for over 90 days.
- Data Loader batch imports failing with cryptic validation or ID truncation errors.
- Unindexed report filters causing slow-loading executive dashboards.

This toolkit provides automated diagnostic scanning scripts to help support engineers advise clients on best practices and proactively resolve tickets.
