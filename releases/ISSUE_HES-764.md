---
issue_id: HES-764
latest_deploy: 20260319T150619Z
category: Improvement
user_facing: 'true'
components:
- dashboard-api
component: dashboard-api
deployments:
- component: dashboard-api
  sha: 9de0bc5955e3f865568977448c313465adfc3a13
  deploy_time: 20260319T150619Z
  pr: '149'
  environment: production
---

# Enhanced Accuracy for Statement Date Queries

**Date:** Mar 19, 2026  
**Category:** Improvement

The logic for filtering statements by date has been enhanced. This update ensures that when you query for statements on a specific date, the system now uses an inclusive range, improving the accuracy and consistency of your compliance data. You will now see more comprehensive results for date-specific queries.

_More details or escalation info here as appropriate._
