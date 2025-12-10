---
issue_id: HES-601
latest_deploy: 20251210T100516Z
category: Feature
user_facing: 'true'
components:
- dashboard-ui
- dashboard-api
component: dashboard-ui, dashboard-api
deployments:
- component: dashboard-ui
  sha: def456
  deploy_time: 20251210T050038Z
  pr: '98'
  environment: production
- component: dashboard-api
  sha: abc123d
  deploy_time: 20251210T061052Z
  pr: '97'
  environment: production
---

# ChemTrack Performance Monitoring and Enhanced Data Accuracy

**Date:** Dec 10, 2025  
**Category:** Feature

Administrators can now access ChemTrack Cache Performance Monitoring within System Settings, providing critical insights through summary cards, a metrics table, and real-time statistics. To ensure enhanced data reliability, chemical amount calculations have been refined for greater consistency and precision. The system intelligently prioritizes the most representative chemical amount and streamlines emissions logic, ensuring reported totals accurately reflect constituent weight.

_More details or escalation info here as appropriate._
