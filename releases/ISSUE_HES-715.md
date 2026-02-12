---
issue_id: HES-715
latest_deploy: 20260212T190733Z
category: Security
user_facing: 'true'
components:
- dashboard-api
component: dashboard-api
deployments:
- component: dashboard-api
  sha: 3bf412501d7323a8e7506a5459a1dcc2759f6730
  deploy_time: 20260212T190733Z
  pr: '117'
  environment: production
---

# Enhanced User Management, Archiving, and Email Security

**Date:** Feb 12, 2026  
**Category:** Security

We've enhanced user account management with immediate access blocking for archived users and a clear, sequential process for archiving, restoring, and permanently deleting accounts. Email changes made by administrators now require user verification before access is restored, and the previous email owner will be notified for increased transparency. We've also strengthened admin permission controls for critical user actions, ensuring proper authorization.

_More details or escalation info here as appropriate._
