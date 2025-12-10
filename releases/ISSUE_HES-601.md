---
issue_id: HES-601
latest_deploy: 20251210T061052Z
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

We're excited to introduce a powerful combination of enhancements for our ChemTrack platform, designed to deliver unparalleled insights and ensure data integrity.  First, we're deploying our new **ChemTrack Cache Performance Monitoring** feature. This robust solution offers administrators critical insights directly within System Settings through a dedicated new page. This page integrates intuitive summary cards, a detailed cache metrics table, and insightful rollup statistics. Powered by a new, robust backend API with real-time data fetching and a React Query hook that includes periodic auto-refresh and company-level data scoping, administrators can now effortlessly monitor vital ChemTrack cache lifecycle and performance metrics.  Complementing this, we've implemented significant **refinements to our chemical amount calculation processes**. These updates enhance the consistency and precision of how chemical amounts are processed and formatted within the ChemTrack system. This includes the introduction of a new helper method to intelligently prioritize `constsum` 'high' values when available and applicable, ensuring the most accurate representation of chemical amounts. Additionally, we've clarified emissions calculation logic to ensure `chem_record[:amount]` accurately represents constituent weight, streamlining our processing.  Together, these advancements empower administrators with both detailed operational oversight and greater confidence in the foundational data accuracy of ChemTrack. This ensures optimal system operation, proactive management, and the highest level of data reliability for your EHS platform. The monitoring feature is seamlessly integrated into the System Settings UI with a new dedicated card and navigation, offering an effortless experience.

_More details or escalation info here as appropriate._
