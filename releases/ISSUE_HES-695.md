---
issue_id: HES-695
latest_deploy: 20260317T143515Z
category: Security
user_facing: 'true'
components:
- dashboard-webapp
component: dashboard-webapp
deployments:
- component: dashboard-webapp
  sha: 286bc8c5d2b25c34a2631898014a06793c9caebd
  deploy_time: 20260317T143515Z
  pr: '740'
  environment: production
---

# Improved Security for External Action Item Links

**Date:** Mar 17, 2026  
**Category:** Security

External links to action items have been enhanced for improved security and reliability. All links, including those in email notifications, now utilize a robust, token-based system with strengthened expiration and validation. This ensures more secure and consistent access for external users managing compliance tasks.

_More details or escalation info here as appropriate._
