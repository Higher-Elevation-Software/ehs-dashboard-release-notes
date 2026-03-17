---
issue_id: HES-695
latest_deploy: 20260317T163419Z
category: Improvement
user_facing: 'true'
components:
- dashboard-webapp
component: dashboard-webapp
deployments:
- component: dashboard-webapp
  sha: 4bd25396250d21ac4b1390393a6e2ca3206a81c6
  deploy_time: 20260317T163419Z
  pr: '760'
  environment: production
---

# Consistent Facility Selection and Data Input Experience

**Date:** Mar 17, 2026  
**Category:** Improvement

We've enhanced how the platform manages facility selections. If a specific facility is unavailable or referenced incorrectly, the system will now automatically default to the first accessible facility, preventing errors and ensuring smoother navigation. This improvement also ensures data input forms consistently display relevant metric categories based on the active facility.

_More details or escalation info here as appropriate._
