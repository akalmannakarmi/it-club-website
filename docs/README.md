# Project Documentation

This documentation set explains **what the IT Club Website does**, **how it is
logically designed**, and **how data flows through it**. It is written for
contributors, club admins, and anyone who wants to understand the system
without reading every line of code.

## What is this project?

A Django-based CMS website for a college IT Club. It combines:

- a **public marketing site** whose sections (banner, about, activities,
  upcoming events, projects, resources, footer) can be turned on/off and
  re-ordered by admins without touching code;
- a **members-only dashboard** for managing members, events, projects,
  resources, sessions and attendance;
- an **automatic audit trail** recording who created/updated/deleted every
  record;
- **email notifications** for registration, approval and password reset;
- a **deployment pipeline** from GitHub to Docker Hub to Kubernetes;

It is designed to be *flexible and reusable for other clubs*: club identity,
section visibility and content are all data-driven, not hardcoded.

> Celery and Redis were removed — see
> [`celery-redis-removal.md`](celery-redis-removal.md) for why and how to bring
> them back if ever needed.

## Document map

| Document | Answers |
|---|---|
| [`01-architecture.md`](01-architecture.md) | What the system is made of, app layout, URLs, middleware, tech stack, deployment. |
| [`02-data-model.md`](02-data-model.md) | All data entities, their fields, relationships and the soft-delete/audit base. |
| [`03-logical-decisions.md`](03-logical-decisions.md) | The important design decisions and *why* each was made. |
| [`04-data-flow.md`](04-data-flow.md) | End-to-end flows: registration → approval, login, dashboard, analytics, emails, deployment. |
| [`environment-variables.md`](environment-variables.md) | Every env var the system reads. |
| [`how-to-run.md`](how-to-run.md) | Running locally and in Docker. |
| [`celery-redis-removal.md`](celery-redis-removal.md) | Why Celery/Redis were removed and how to re-enable them. |

## Quick facts

- **Framework:** Django 5.2 / Python 3.14
- **Database:** MySQL in Docker/production, SQLite by default locally
  (`DATABASE_MODE` env switch)
- **Background tasks:** none — Celery + Redis were removed
  ([`celery-redis-removal.md`](celery-redis-removal.md))
- **Auth:** login by **email** (no username), roles are Django `Group`s
  (`"Admin"`, `"Member"`)
- **Data safety:** soft delete + automatic `AuditLog` on every record
- **Deploy:** push to `main` → GitHub Actions builds/pushes a Docker Hub image
  → `kubectl set image` rollout on Kubernetes

> Note: `/events/` and `/resource/` are working public landing pages; the
> `/announcement/` route was removed.
