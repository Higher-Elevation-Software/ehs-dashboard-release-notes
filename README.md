# EHS Dashboard Release Notes

Automated public changelog aggregator for the EHS Dashboard ecosystem.

**Live Site**: https://higher-elevation-software.github.io/ehs-dashboard-release-notes/

## Overview

This repository serves as a central aggregator for release notes from all EHS Dashboard services. When services deploy to production, they automatically trigger a `repository_dispatch` event that creates a new release note entry and regenerates the public changelog.

## Architecture

```
Service Deploy (Cloud Build/GitHub Actions)
    ↓
Repository Dispatch Event
    ↓
Aggregator Workflow (.github/workflows/aggregate-on-dispatch.yml)
    ↓
Creates releases/*.md file
    ↓
Regenerates index.md
    ↓
Commits & Pushes to main
    ↓
GitHub Pages Publishes
```

## Service Integration

Services integrate by sending a `repository_dispatch` event after successful production deployment.

### Required Payload Fields

- **component** (string, required): Service identifier (e.g., `dashboard-api`, `dashboard-webapp`, `dashboard-ui`)
- **sha** (string, required): Git commit SHA of the deployed code
- **title** (string, required): Human-readable title for the release note

### Optional Payload Fields

- **summary** (string): Detailed description (defaults to title)
- **pr** (string): Pull request number
- **deploy_time** (string): UTC timestamp in format `YYYYMMDDTHHMMSSZ` (defaults to current time)
- **environment** (string): Deployment environment (defaults to `production`)

### Example: Cloud Build Integration

Add this step at the end of your `cloudbuild.yaml`:

```yaml
- name: gcr.io/cloud-builders/curl
  id: notify-changelog
  env:
    - COMMIT_SHA=${COMMIT_SHA}
  secretEnv: ['AGGREGATOR_TOKEN']
  entrypoint: bash
  args:
    - -c
    - |
      TITLE=$(git log -1 --pretty=%s "$COMMIT_SHA" || echo "Production deployment")
      SUMMARY=$(git log -1 --pretty=%b "$COMMIT_SHA" || echo "$TITLE")
      PR=$(echo "$SUMMARY" | grep -oP '(?<=#)\d+' | head -1 || echo "")
      
      curl -X POST \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $$AGGREGATOR_TOKEN" \
        https://api.github.com/repos/Higher-Elevation-Software/ehs-dashboard-release-notes/dispatches \
        -d "{
          \"event_type\": \"release-note\",
          \"client_payload\": {
            \"component\": \"your-service-name\",
            \"sha\": \"$COMMIT_SHA\",
            \"title\": \"$(echo "$TITLE" | jq -Rs .)\",
            \"summary\": \"$(echo "$SUMMARY" | jq -Rs .)\",
            \"pr\": \"$PR\",
            \"environment\": \"production\"
          }
        }"

availableSecrets:
  secretManager:
    - versionName: projects/YOUR_PROJECT/secrets/AGGREGATOR_TOKEN/versions/latest
      env: AGGREGATOR_TOKEN
```

### Example: GitHub Actions Integration (Vercel)

Add this workflow to `.github/workflows/` in your repo:

```yaml
name: Release Note on Deploy
on:
  push:
    branches: [main]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Wait for Vercel deployment
        # Add Vercel deployment waiting logic here
        
      - name: Dispatch release note
        run: |
          curl -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token ${{ secrets.AGGREGATOR_TOKEN }}" \
            https://api.github.com/repos/Higher-Elevation-Software/ehs-dashboard-release-notes/dispatches \
            -d '{
              "event_type": "release-note",
              "client_payload": {
                "component": "your-service-name",
                "sha": "${{ github.sha }}",
                "title": "${{ github.event.head_commit.message }}",
                "environment": "production"
              }
            }'
```

## Testing

Use the provided test script to manually trigger a release note:

```bash
./test-dispatch.sh my-component abc123 "My Test Release"
```

Or manually with `curl`:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $(gh auth token)" \
  https://api.github.com/repos/Higher-Elevation-Software/ehs-dashboard-release-notes/dispatches \
  -d '{
    "event_type": "release-note",
    "client_payload": {
      "component": "test-component",
      "sha": "abc123",
      "title": "Test Release"
    }
  }'
```

## Secrets & Permissions

### AGGREGATOR_TOKEN

A GitHub Personal Access Token (fine-grained) with:
- **Repository access**: Only `Higher-Elevation-Software/ehs-dashboard-release-notes`
- **Permissions**: Contents (Read and Write)

This token must be:
1. Stored in GCP Secret Manager as `AGGREGATOR_TOKEN` for Cloud Build services
2. Stored as a GitHub Repository Secret in each service repo that uses GitHub Actions

### Rotating the Token

1. Generate a new fine-grained PAT in GitHub with the same permissions
2. Update the secret in GCP Secret Manager:
   ```bash
   echo -n "NEW_TOKEN" | gcloud secrets versions add AGGREGATOR_TOKEN --data-file=-
   ```
3. Update GitHub Repository Secrets for each service using GitHub Actions

## File Structure

- `.github/workflows/aggregate-on-dispatch.yml` - Main aggregator workflow
- `releases/` - Individual release note files (auto-generated)
- `index.md` - Main changelog page (auto-generated)
- `.nojekyll` - Disables Jekyll processing for GitHub Pages
- `test-dispatch.sh` - Manual testing script

## Workflow Details

The aggregator workflow:
1. **Validates** incoming payload (component, sha, title required)
2. **Creates** a release note file: `releases/YYYYMMDDTHHMMSSZ_component_sha.md`
3. **Regenerates** `index.md` with links to all release notes
4. **Commits** and pushes changes to main branch
5. **Triggers** GitHub Pages rebuild

## Troubleshooting

### Dispatch not triggering workflow

- Verify `AGGREGATOR_TOKEN` has correct permissions
- Check if GitHub Actions are enabled for the repository
- Confirm the payload includes required fields (component, sha, title)
- Look for rate limiting (5000 API requests per hour per token)

### Release note not appearing on site

- Check workflow runs: https://github.com/Higher-Elevation-Software/ehs-dashboard-release-notes/actions
- Verify the workflow completed successfully
- Check Pages deployment status
- Clear browser cache if recently deployed

### Workflow failing

- Review workflow run logs in GitHub Actions
- Verify the Python script has all required environment variables
- Check git commit/push permissions

## Monitoring

- **Workflow Runs**: https://github.com/Higher-Elevation-Software/ehs-dashboard-release-notes/actions/workflows/aggregate-on-dispatch.yml
- **Live Site**: https://higher-elevation-software.github.io/ehs-dashboard-release-notes/
- **GitHub Pages**: Settings → Pages in this repository

## Future Enhancements

- [ ] Add status-page integration (currently undecided)
- [ ] Email notifications on deployment
- [ ] Slack webhook integration
- [ ] Deployment metrics dashboard
- [ ] Rollback detection and alerting
