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

- **Component** – which part of the system changed
- **SHA** – the commit identifier for the deployed code
- **Deployed** – UTC timestamp of the deployment
- **Environment** – currently always `production` for public entries
- **Summary** – a short description of the change

You can browse individual release files under the
[`releases/`](./releases) directory, or use the
[main changelog page](https://higher-elevation-software.github.io/ehs-dashboard-release-notes/)
for a chronological view.

---

## How to read a release entry

On the changelog site you will see entries like:

> `20251204T185423Z_dashboard-webapp-_4481952.md — Send staging release notes to main branch; only environment varies`

Clicking a link opens the full release note. Each note shows:

- A **title** describing the change
- The affected **component**
- The deployed **commit SHA**
- The **deployment time** in UTC
- The **environment** (production)
- A short **summary** providing additional context

If you need more information about a particular change (for example,
which ticket, feature, or pull request it corresponds to), please
contact your EHS representative or open an issue in the relevant service
repository.

---

## Update frequency

The changelog is updated automatically when a production deployment of
any of the services above completes successfully. The site is typically
refreshed within a minute of a deployment finishing.

There is no manual curation step between deployment and publication;
entries are generated directly from the deployment pipelines.

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
