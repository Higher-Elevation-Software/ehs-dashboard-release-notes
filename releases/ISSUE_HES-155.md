---
issue_id: HES-155
latest_deploy: 20260330T153436Z
category: Improvement
user_facing: 'true'
components:
- dashboard-api
component: dashboard-api
deployments:
- component: dashboard-api
  sha: 8ba70218ca297caf0cd7cbe384bea721fbdfc809
  deploy_time: 20260330T153436Z
  pr: '156'
  environment: production
---

# Improved Widget XLSX Export Reliability and Filenames

**Date:** Mar 30, 2026  
**Category:** Improvement

Widget data exports to XLSX now consistently generate valid files, even for widgets with long titles. If an export cannot be generated, users will receive a clear error response instead of an empty download. Downloaded files also display the intended server-provided filename.

_More details or escalation info here as appropriate._
