#!/bin/bash
# Test script for triggering release note repository dispatch events
# Usage: ./test-dispatch.sh [component] [sha] [title]

set -euo pipefail

COMPONENT="${1:-test-component}"
SHA="${2:-$(git rev-parse HEAD 2>/dev/null || echo 'abc123def456')}"
TITLE="${3:-Test Release Note}"
SUMMARY="${4:-This is a test release note triggered manually}"
PR="${5:-}"
ENVIRONMENT="${6:-production}"

# Get current UTC timestamp
DEPLOY_TIME=$(date -u +%Y%m%dT%H%M%SZ)

echo "Triggering release note dispatch..."
echo "  Component: $COMPONENT"
echo "  SHA: $SHA"
echo "  Title: $TITLE"
echo "  Deploy time: $DEPLOY_TIME"
echo "  Environment: $ENVIRONMENT"
echo

# Send the dispatch
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $(gh auth token)" \
  https://api.github.com/repos/Higher-Elevation-Software/ehs-dashboard-release-notes/dispatches \
  -d "{
    \"event_type\": \"release-note\",
    \"client_payload\": {
      \"component\": \"$COMPONENT\",
      \"sha\": \"$SHA\",
      \"title\": \"$TITLE\",
      \"summary\": \"$SUMMARY\",
      \"pr\": \"$PR\",
      \"deploy_time\": \"$DEPLOY_TIME\",
      \"environment\": \"$ENVIRONMENT\"
    }
  }"

echo
echo "Dispatch sent! Check workflow runs:"
echo "  https://github.com/Higher-Elevation-Software/ehs-dashboard-release-notes/actions/workflows/aggregate-on-dispatch.yml"
echo
echo "Or run: gh run list --workflow=aggregate-on-dispatch.yml --event repository_dispatch --limit 1"
