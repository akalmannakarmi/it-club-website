# 3 · Logical Decisions

This page records the notable design decisions, the reasoning behind them, and
their consequences. Code references point to the file/line that implements each
decision.

---

## 1. Custom user model — login by email, no username

**Decision:** `AUTH_USER_MODEL = "user.User"` (`config/settings.py`), a
subclass of `AbstractUser` with `username = None` and
`USERNAME_FIELD = "email"` (`user/models.py`).

**Why:** Club members identify each other by email, not a chosen username.
Email is guaranteed unique and there's nothing to forget or collide over.
Keeping `AbstractUser` as the base preserves Django's password hashing,
`is_staff`/`is_superuser`, and permission plumbing.

**Consequences:** The custom `LoginForm` looks the user up by email then calls
`authenticate(email=…, password=…)`. `create_user` requires an email.
Registrations must collect `faculty`/`batch`/`phone` in addition to the
standard name fields. `REQUIRED_FIELDS` stays empty because email is the
username field.

---

## 2. Roles are Django `Group`s, not permissions

**Decision:** Exactly two groups exist — `"Admin"` and `"Member"` — created by
the idempotent `add_groups` management command and by `get_or_create` at
runtime. Views are guarded by mixins in `user/mixins.py`
(`AdminRequiredMixin`, `MemberRequiredMixin`, `AdminOrOwnerRequiredMixin`);
templates receive `is_admin`/`is_member` from `user/context_processors.py`.

**Why:** The club needs a simple two-tier hierarchy (staff vs members). Django
permissions-per-action would be overkill; group membership answers "can this
user see/do this" in one query and is editable from the Django admin.

**Consequences:**
- `MemberRequiredMixin` = groups `["Admin", "Member"]` (admins can do anything
  members can).
- `AdminRequiredMixin` = groups `["Admin"]`.
- Superusers are added to `"Admin"` automatically in
  `UserManager.create_superuser`.
- A user's *group* does not control login — that is the `is_active` flag (see
  decision 3).

---

## 3. Open registration, admin-approved activation

**Decision:** Self-registration (`RegisterView`) creates the user with
`is_active = False` and adds them to `"Member"`. Only an admin can flip
`is_active` via the dashboard (`MemberActivateView`/`MemberDeactivateView`).

**Why:** The site wants anyone from the college to be able to sign up, but the
club needs to verify members before granting access to internal data. Because
Django's `authenticate()` refuses inactive users, an unapproved account simply
cannot log in — no extra gate needed.

**Consequences:**
- Emails on registration: the applicant gets "registration received"; admins
  get "new member registration".
- Activation/deactivation emails are sent when an admin toggles the flag.
- `MemberForm` (dashboard create/edit) exposes `is_active` directly, and the
  create view assigns the `"Member"` group.
- "Member list" and attendance views only count/show `is_active=True` users.

---

## 4. Soft delete everywhere

**Decision:** All content models inherit `BaseModel` (`audit/models.py`) with a
`deleted_at` timestamp. `delete()` stamps `deleted_at` instead of removing the
row. The default manager `objects` filters out deleted rows; `objects_all`
returns everything.

**Why:** Club records (members, projects, attendance) are worth preserving. A
misclicked delete shouldn't destroy data, and history should be recoverable.
Soft delete also keeps historical foreign-key links (e.g. a member who
attended sessions) intact.

**Consequences:**
- `User` overrides the manager (`UserManager`) so its own `objects` also hides
  deleted users; deactivated ≠ deleted.
- Admin views use `objects` so deleted rows vanish from normal lists; the
  audit log still references their IDs.
- Counts/statistics never include soft-deleted records.

---

## 5. Automatic audit logging on every write

**Decision:** `BaseModel.save()` and `BaseModel.delete()` automatically insert
an `AuditLog` row. `save()` distinguishes `create` vs `update`; it stores a
full JSON snapshot of every field and M2M relation. `delete()` records action
`delete`. The acting user comes from thread-locals set by
`CurrentUserMiddleware` (`audit/middleware/current_user.py`).

**Why:** Accountability for a small team. Anyone who changes content is
recorded with exactly what the record looked like, without developers having
to remember to call an auditing function everywhere.

**Consequences:**
- `no_audit=True` on `save()` is used internally (e.g. by `delete()`) to avoid
  double logging.
- `AuditLog` itself is deliberately *not* a `BaseModel`, so logs are never
  soft-deleted or re-audited.
- The dashboard shows this feed in the audit list view with free-text search.
- JSON `changes` means full-row "before/after-style" snapshots are already
  captured (note: a single snapshot of the *resulting* row per action, not a
  before/after diff).

---

## 6. Singleton configuration rows

**Decision:** `PageSettings` and `AboutUs` are singletons: `save()` forces
`pk = 1` (`pages/models.py`), and the dashboard views use
`get_or_create(pk=1)` (`dashboard/views.py`). `PageSettings` is cached in the
in-memory cache for 1 hour by `pages/context_processors.py` and the cache is
purged on save.

**Why:** Exactly one site-wide config and one "about" blob can exist; singletons
avoid ID confusion and duplicate rows. Caching means the most-read row on the
site (rendered on every page for the navbar title/icon) costs one query per
hour instead of one per request.

**Consequences:**
- First visit to an empty database lazily creates the singleton (`get_or_create`),
  so no data seeding is required to boot.
- Any save invalidates the cache so changes appear quickly.
- `send_html_email` reuses `page_settings()` to inject branding into emails.

---

## 7. CMS-style homepage driven by visibility flags

**Decision:** The homepage (`IndexView` → `templates/pages/default/index.html`)
renders each section conditionally on a `PageSettings.show_*` boolean
(`show_banner`, `show_about`, `show_whatwedo`, `show_upcoming`, `show_projects`,
`show_resources`, `show_events`, `show_footer`).

**Why:** The stated goal is a site reusable by *other clubs*. Layout is
configuration, not code: an admin can hide the "projects" section entirely or
recompose the homepage without a developer.

**Consequences:**
- Each content model also has `display` (show this specific item) and `order`
  (sort position) fields — a per-item layer on top of the per-section flag.
- Public queries filter `display=True` and `order_by("order")`.

---

## 8. Per-item `display` + `order` pattern

**Decision:** `WhatWeDo`, `Event`, `Project`, and `Resource` all carry
`order = IntegerField(default=0)` and `display = BooleanField(default=True)`,
and the homepage sorts by `order` while filtering `display`.

**Why:** Gives admins fine-grained control — hide a stale project, pin a
featured event to the front — while keeping one consistent convention across
all content types. Sliders pick up the sorted list directly.

---

## 9. `DATABASE_MODE` env switch + PyMySQL driver

**Decision:** `DATABASE_MODE=mysql` (Docker/prod) selects the MySQL backend with
utf8mb4 + `STRICT_TRANS_TABLES`; anything else selects SQLite
(`config/settings.py`). `config/__init__.py` runs `pymysql.install_as_MySQLdb()`
so Django uses PyMySQL; `mysqlclient` must never be added.

**Why:** Local development should be zero-infrastructure (a file-based SQLite
DB), while Docker/production needs a real server with MySQL 8. PyMySQL is a
pure-Python driver that installs cleanly cross-platform — a real convenience
for Windows contributors, for whom `mysqlclient` needs a C compiler.

**Consequences:** Env `MYSQL_*` variables are only read in `mysql` mode; the
`example.env` defaults to `mysql` (matching the compose stack), so local devs
must set `DATABASE_MODE=sqlite`.

---

## 10. Email via Gmail SMTP, branded multipart messages

**Decision:** `EMAIL_BACKEND` is SMTP to `smtp.gmail.com:587` with TLS; a single
helper `send_html_email()` (`user/utils/email.py`) renders an HTML template
plus a plain-text fallback and always injects `page_settings` and the
request's protocol/domain.

**Why:** The club runs on a Gmail address (app password), and every email —
registration, approval, reset — should look consistent with the site, including
absolute links in a world of HTTP/HTTPS.

**Consequences:** `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` must be set or all
emailing silently fails (the callers `try/except` and log). Password reset uses
Django's built-in views with overridden subject and HTML templates.

---

## 11. No Celery / Redis — background tasks removed

**Decision:** Celery, Redis, and `django-celery-beat` were removed. There is no
background-task infra today: `config/celery.py`, `events/tasks.py` (a stub
`scrape_task`), the `CELERY_*` settings, and the compose `celery`/`celery-beat`/
`redis` services are gone. See
[`celery-redis-removal.md`](celery-redis-removal.md) for the full record and the
re-enable recipe.

**Why:** Production deploys to a cPanel Python web app, where standing up and
running Redis + a Celery worker/beat is disproportionate to the only task that
existed (a placeholder `print` stub). Removing it eliminates the broker
dependency, ~19 unneeded `requirements.txt` packages, and the fresh-DB migration
blocker (`events.0001_initial` used to depend on `django_celery_beat`, which
failed `migrate` on a database that never had that app).

**Consequences:** No scheduled/background work can run without re-adding the
stack. Re-adding is a documented, reversible procedure (new migration to
re-create the schedule, packages, settings, `config/celery.py`, a real task).
Any DB that already applied the old `django_celery_beat` migrations keeps its
orphaned tables — harmless, and droppable manually.

---

## 12. Whitenoise manifest static files; media only in DEBUG

**Decision:** `STATICFILES_STORAGE =
whitenoise.storage.CompressedManifestStaticFilesStorage`, `collectstatic`
runs in `entrypoint.sh`, and `/media/` is served by Django **only** when
`DEBUG=True` (`config/urls.py`).

**Why:** Static assets should be served by the app itself (no separate CDN/web
server in the K8s setup), and Whitenoise's manifest hashing gives cache-busting
without an extra proxy. Media uploads are served directly only in dev because
production is expected to place media behind the ingress/object storage later.

**Consequences:** Running prod without `collectstatic` breaks asset URLs; a
known bootstrap step in `entrypoint.sh` handles this.

---

## 13. Bikram Sambat batch years

**Decision:** Batch options run from **2068 BS** to the current Gregorian year
**+ 57** (`User.batch_choices()`, `user/models.py`), and the college faculty
choices are `CSIT, BCA, BBS, BBM, MBA, BIT` (`User.FACULTY_CHOICES`).

**Why:** Nepali college admissions are labeled by the Bikram Sambat calendar
(≈ Gregorian + 57 years); 2068 BS is the "oldest" active batch and the end is
computed live so new academic years appear without a migration.

**Consequences:** Choices are regenerated dynamically wherever a form renders
them (registration, member forms, list filters), so a new batch year "just
appears" on its due date.

---

## 14. Attendance as a `Session` ↔ `User` many-to-many + engagement analytics

**Decision:** `Session` has `date`, `title`, `description` and an `attendees`
M2M to `User` (`attendance/models.py`). The dashboard derives all metrics from
this single relation:
- "Active members" = users who attended any of the last 3 sessions;
- "Attendees (last 30 days)" and its % change vs the prior 30 days
  (`DashboardView`);
- Per-member attendance % = `attended_sessions_count / total_sessions`
  (`AttendanceListView`);
- A per-session attended/not-attended matrix (`AttendanceDetailView`,
  `MyAttendanceDetailView`).

**Why:** A single source of truth for "who shows up" powers both admin
oversight and member self-service, and drives the club's engagement KPIs. The
M2M gives bidirectional queries (sessions a member attended vs attendees of a
session) with no extra table.

**Consequences:** Admins record attendance by editing a session's attendee
checkbox list (the session form passes active members). Attendance pages only
list active members.

---

## 15. Ownership-aware project access

**Decision:** `ProjectDetailView` uses `AdminOrOwnerRequiredMixin`, which allows
admins *or* the project's `supervisor`/`members` to view it. `MyProjectListView`
shows a user the projects where they are supervisor or a member.

**Why:** Project details (links, repos, tech stack) are semi-private team
context. Members should see their own work; only admins see everything.

---

## 16. Bootstrap ordering in the container

**Decision:** `entrypoint.sh` runs `collectstatic` → `migrate` → `add_groups`
→ server (Gunicorn unless `DEBUG`).

**Why:** A fresh deploy needs assets collected, schema migrated, and groups
created before serving traffic. Making it the entrypoint means deploys are
self-healing — no manual `manage.py` steps on the cluster.

---

## 17. CI/CD: push to `main` → Docker Hub → Kubernetes

**Decision:** GitHub Actions (`docker-publish.yml`) builds and pushes
`it-club-website:latest` + `:sha` to Docker Hub, then runs
`kubectl set image deployment/it-club-website …` and waits for rollout.

**Why:** `main` is the production branch; every merged PR is deployable. Image
tags by git SHA allow instant rollback by re-pointing the deployment at an
older tag.

**Consequences:** Secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`,
`KUBECONFIG_BASE64`) live in GitHub secrets. Feature work happens on
`feat/…`/`fix/…` branches and merges via PR (a `prod` branch also exists for
alternate release workflows).

---

## 18. LocMemCache for the most-read row

**Decision:** `PageSettings` is cached with the default `LocMemCache` (per-process
in-memory) for one hour and purged on save (`pages/models.py`,
`pages/context_processors.py`).

**Why:** Cheapest correct approach for a single-replica app — no cache
round-trip for the one value every page needs. (Redis/Celery were removed, so
the in-memory cache is the only cache in play.)

**Consequence:** With multiple web replicas each process caches its own copy;
cache invalidation only clears the local process. Acceptable at this scale, but
a distributed cache should be revisited if the deployment grows.

---

## 19. Production security hardening in settings

**Decision:** `config/settings.py` now fails loudly outside DEBUG mode when
`SECRET_KEY` is unset (`ImproperlyConfigured`), `DEBUG` defaults to `FALSE`,
and a `if not DEBUG:` block applies HTTPS-only hardening:
`SECURE_SSL_REDIRECT`, HSTS (1 year + subdomains), `SECURE_CONTENT_TYPE_NOSNIFF`,
`SECURE_REFERRER_POLICY = "same-origin"`, secure session/CSRF cookies, and
`SECURE_PROXY_SSL_HEADER` (TLS is terminated before gunicorn on cPanel).

**Why:** A missing env var in production should not silently fall back to a
public key and debug-on tracebacks. These settings are safe on Django 5.2 and
only active when `DEBUG` is off.

**Consequence:** Production deploys must export `SECRET_KEY` and set
`DEBUG=FALSE` (or omit it). HSTS is sent once HTTPS is proven stable; revisit
`SECURE_HSTS_PRELOAD` only when ready to commit to the preload list.

---

## 20. Timezone is `Asia/Kathmandu`

**Decision:** `TIME_ZONE = "Asia/Kathmandu"` (was `UTC`), `USE_TZ` stays `True`.

**Why:** The club is in Nepal; admin-entered `datetime-local` values are now
interpreted and displayed in Kathmandu time instead of shifting by +5:45.

**Consequence:** Values are still stored as absolute UTC timestamps in the DB,
so existing rows are unaffected — only display/interpretation changed. No
migration required.

---

## 21. Tailwind CDN is dev-only; CDN assets are SRI-pinned

**Decision:** The `cdn.tailwindcss.com` JIT script in `templates/base.html` is
**dev-only** — it compiles styles at runtime in the browser, which is slow and
fragile for production. It is intentionally kept for now; switching to a
compiled CSS pipeline (e.g. a build step producing a static stylesheet) is the
intended future change and is **out of scope** for the current pass.

**Why:** Building the Tailwind toolchain is a larger change; keeping the dev
script is the documented interim state rather than a silent regression.

**Consequence:** Before any production launch, replace the Tailwind JIT CDN
script with a compiled stylesheet.

**Decision (same entry):** Third-party assets loaded from CDNs are pinned to
exact versions with SRI `integrity` + `crossorigin="anonymous"`:
Swiper `10.3.1`, AOS `2.3.4`, Chart.js `4.4.1` (`dist/chart.umd.min.js`). The
previous unpinned `https://cdn.jsdelivr.net/npm/chart.js` (floating latest)
was a supply-chain risk.

**Why:** SRI guarantees the served bytes match the expected hash; pinning stops
floating-version drift. Vendoring these files into `static/vendor/` is a
possible future step to drop the internet dependency entirely.

