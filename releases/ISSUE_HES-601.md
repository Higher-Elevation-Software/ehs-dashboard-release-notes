---
issue_id: HES-601
latest_deploy: 20251210T064232Z
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

# Comprehensive ChemTrack Insights: Performance Monitoring & Enhanced Data Precision

**Date:** Dec 10, 2025  
**Category:** Feature

We're excited to introduce **ChemTrack Cache Performance Monitoring**, a robust new feature for administrators accessible within System Settings. This provides critical insights through intuitive summary cards, a detailed cache metrics table, and rollup statistics, powered by a new backend API for real-time, auto-refreshing data on cache lifecycle and performance. Complementing this, we've also implemented significant **refinements to our chemical amount calculation processes**, enhancing the consistency and precision of how chemical amounts are processed and formatted. These updates include an optimized approach to intelligently prioritize the most representative values and clarified emissions calculation logic, ensuring reported chemical amounts accurately reflect constituent weight for greater data reliability. Together, these advancements empower administrators with both detailed operational oversight and greater confidence in the foundational data accuracy of ChemTrack, ensuring optimal system operation and the highest level of data reliability for your EHS platform.

_More details or escalation info here as appropriate._
