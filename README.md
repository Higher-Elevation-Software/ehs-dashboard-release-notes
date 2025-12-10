# EHS Dashboard — Release Notes

This repository powers the **public changelog** for the EHS Dashboard
suite of services.

**Live changelog:**  
https://higher-elevation-software.github.io/ehs-dashboard-release-notes/

Whenever we deploy a new version of one of our production services, an
automated process creates a release note in this repository and updates
the public site.

---

## What this site covers

The changelog currently includes production releases for:

- `dashboard-api` – core backend API
- `dashboard-webapp` – main web application
- `dashboard-ui` – dashboard user interface

Only **production** deployments are recorded here. Staging and internal
previews are not included.

Each release note contains:

- **Component(s)** – which part(s) of the system changed
- **SHA(s)** – the commit identifier(s) for the deployed code
- **Deployed** – UTC timestamp of the deployment
- **Environment** – currently always `production` for public entries
- **Category** – Feature, Improvement, Security, or Internal
- **Summary** – a short description of the change

**Note:** When multiple services deploy changes for the same feature
(identified by a HES-XXX issue ID), they are automatically merged into a
single release note showing all affected components and their respective
commit SHAs.

You can browse individual release files under the
[`releases/`](./releases) directory, or use the
[main changelog page](https://higher-elevation-software.github.io/ehs-dashboard-release-notes/)
for a chronological view.

---

## How to read a release entry

On the changelog site, each release card shows:

- A **title** describing the change
- The affected **component(s)** (e.g., dashboard-api, dashboard-ui)
- The **category badge** (Feature, Improvement, Security, or Internal)
- The **environment** badge (production or staging)
- The **deployment date**
- Click to expand for a detailed **summary** and **commit SHA(s)**

**Multi-component releases:** When a feature affects multiple services,
you'll see multiple component badges and multiple SHA badges (labeled
with their respective components) in the expanded view.

If you need more information about a particular change (for example,
which ticket, feature, or pull request it corresponds to), please
contact your EHS representative or open an issue in the relevant service
repository.

---

## Update frequency

The changelog is updated automatically when a production deployment of
any of the services above completes successfully. The deployment triggers
an automated workflow that:

1. Detects if the change is part of a tracked feature (HES-XXX issue)
2. Generates or updates a release note with AI-enhanced messaging
3. Creates a pull request for team review
4. After PR approval, the site is refreshed within a minute

This process ensures release notes are accurate and professionally
written while maintaining automation.

---

## Feedback & support

If you notice something incorrect in the release notes, or need more
information about a change:

- Open an issue in this repository, **or**
- Contact your EHS account representative.

---

## For developers

This repository is maintained by the EHS engineering team.

If you are integrating a new internal service with the changelog system,
see:

- [`docs/INTERNALS.md`](./docs/INTERNALS.md) – internal integration
details (payload format, examples, and secret management).
