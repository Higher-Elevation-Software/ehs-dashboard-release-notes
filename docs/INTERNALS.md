# EHS Dashboard Release Notes – Internal Integration Guide

This document is for **EHS engineers** who integrate services with the
`ehs-dashboard-release-notes` aggregator. It describes the internal
payload format, workflows, and testing tools. It is **not** intended for
external clients.

For a public overview of the project, see the top-level `README.md`.

---

## Architecture

```
Service Deploy (Cloud Build / GitHub Actions)
    ↓
Repository Dispatch Event (event_type: release-note)
    ↓
Aggregator Workflow (.github/workflows/aggregate-on-dispatch.yml)
    ↓
Creates releases/*.md file
    ↓
Regenerates index.md
    ↓
Commits & pushes to target branch (defaults to repo default branch, currently main)
    ↓
GitHub Pages publishes
```

The aggregator workflow is triggered by a GitHub `repository_dispatch`
event with `event_type: release-note`.

---

## Payload format

Services send a `repository_dispatch` event to this repository with the
following JSON payload:

```json
{
  "event_type": "release-note",
  "client_payload": {
    "component": "dashboard-api",
    "sha": "<git sha>",
    "title": "Short human-readable title",
    "summary": "Optional longer summary",
    "pr": "123",
    "deploy_time": "YYYYMMDDTHHMMSSZ",
    "environment": "production",
    "target_branch": "main"
  }
}
```

### Required fields

- `component` – short service identifier
  (e.g. `dashboard-api`, `dashboard-webapp`, `dashboard-ui`).
- `sha` – git commit SHA of the deployed code.
- `title` – human-readable title for the release note.

The workflow will **fail** if any of these are missing or empty.

### Optional fields

- `summary` – longer description; defaults to `title` if omitted.
- `pr` – pull request number as a string.
- `deploy_time` – UTC timestamp (`YYYYMMDDTHHMMSSZ`); defaults to
  the current time on the runner.
- `environment` – logical environment; defaults to `production`.
- `target_branch` – branch to receive the release commit. If omitted,
  the workflow falls back to:
  1. `TARGET_BRANCH_OVERRIDE` (derived from the payload), then
  2. `TARGET_BRANCH` (the repository’s default branch, currently `main`).

For the **EHS Dashboard services** we currently leave `target_branch`
unset and always write to `main`.

---

## What the workflow generates

For each valid dispatch, the aggregator:

1. Creates a release file:
   `releases/YYYYMMDDTHHMMSSZ_<component>_<short-sha>.md`.
2. Writes a YAML front-matter block with `component`, `sha`,
   `deploy_time`, `pr`, and `environment`.
3. Adds a `# <title>` heading followed by details and the `summary`.
4. Regenerates `index.md` with a list of all releases in reverse
   chronological order.
5. Commits the changes and pushes to the chosen target branch.

`index.md` entries are rendered as:

```text
<filename>.md — <first H1 heading from the file>
```

So the **displayed title** in the changelog comes directly from the
`title` field in `client_payload`.

---

## How EHS services integrate today

Current production integrations:

- `dashboard-api`
  - Dispatches from the `master` branch only (Cloud Build trigger).
  - Always sends `environment: production`, `target_branch: main`.
- `dashboard-webapp`
  - Dispatches from the `main` branch only (Cloud Build trigger).
  - Always sends `environment: production`, `target_branch: main`.
- `dashboard-ui`
  - GitHub Actions workflow runs on `push` to `main`.
  - Always sends `environment: production`, `target_branch: main`.

Each service sets `component`, `sha`, `title`, and `summary` based on
its own deployment scripts (typically using `git log -1` for the
subject/body and then cleaning it up as needed).

---

## Local testing

You can manually trigger the workflow using the provided script:

```bash
./test-dispatch.sh my-component abc123 "My Test Release"
# Optionally specify summary, pr, environment, target_branch:
# ./test-dispatch.sh my-component abc123 "My Test Release" "Summary" "" production main
```

This script uses your `gh auth token` to authenticate and sends a
`repository_dispatch` event directly to GitHub.

You can also do the same with raw `curl`:

```bash
DEPLOY_TIME=$(date -u +%Y%m%dT%H%M%SZ)

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $(gh auth token)" \
  https://api.github.com/repos/Higher-Elevation-Software/ehs-dashboard-release-notes/dispatches \
  -d "{
    \"event_type\": \"release-note\",
    \"client_payload\": {
      \"component\": \"test-component\",
      \"sha\": \"abc123\",
      \"title\": \"Test Release\",
      \"deploy_time\": \"$DEPLOY_TIME\"
    }
  }"
```

---

## Secrets & permissions

### `AGGREGATOR_TOKEN`

Services authenticate to GitHub using a fine-grained PAT with:

- **Repository access**: only
  `Higher-Elevation-Software/ehs-dashboard-release-notes`.
- **Permissions**: `contents: read/write`.

This token is stored as:

1. A secret in **GCP Secret Manager** (`AGGREGATOR_TOKEN`) for
   Cloud Build–based services.
2. A **repository secret** for any service using GitHub Actions.

When rotating the token, update both locations.

---

## Troubleshooting

- **Workflow not triggered**
  - Confirm the `event_type` is `release-note`.
  - Ensure the PAT (`AGGREGATOR_TOKEN`) has write access to this repo.
  - Check that GitHub Actions are enabled for the repository.

- **Workflow fails**
  - Inspect the run logs in GitHub Actions.
  - Verify required fields (`component`, `sha`, `title`) are present.
  - Check for git push errors (e.g., branch out of date).

- **Release doesnt appear on the public site**
  - Confirm the workflow run completed successfully.
  - Ensure the commit landed on `main`.
  - Check the most recent GitHub Pages deployment for errors.

---

## Future enhancements (internal)

- Optional staging-only branches for previewing release notes.
- Additional metadata (e.g., linked issues, labels).
- Slack / email notifications on production deploys.
- Automatic cleanup / normalization of titles and summaries.
