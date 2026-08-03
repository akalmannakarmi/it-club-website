# Environment Variables

This document describes the environment variables used by the it-club-website project.

Create a `.env` file in the project root using `example.env` as a reference.

---

## Required Variables

```env
SECRET_KEY=insert_secret_key
DEBUG=TRUE
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
DATABASE_NAME=db.sqlite3
```

---

## Variable Descriptions

- `SECRET_KEY`  
  Django secret key used for cryptographic signing. **Required when `DEBUG`
  is off** — `config/settings.py` raises `ImproperlyConfigured` at startup if
  it is missing outside DEBUG mode. For local dev set `DEBUG=TRUE` and any
  throwaway value.

- `DEBUG`  
  Enables debug mode. Defaults to **`FALSE`** (the safe direction). Set to
  `TRUE` for local development. Production must run with `FALSE`.

- `ALLOWED_HOSTS`  
  Comma-separated list of allowed hostnames.

- `CSRF_TRUSTED_ORIGINS`  
  Required for CSRF protection when running behind proxies or Docker.

- `DATABASE_NAME`  
  SQLite database file name (default setup).

- `DATABASE_MODE`  
  `mysql` (Docker / production) or `sqlite` (local default when unset).

- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`  
  SMTP credentials for sending mail. A single pair is used (python-dotenv keeps
  the **first** occurrence in `.env` — delete duplicate blocks). Gmail's
  **app password** (not the account password) is used with the settings in
  `config/settings.py`.

---

## Notes

- Never commit `.env` files to version control
- Production environments should use stronger secrets and a proper database
- Outside DEBUG mode the app also enforces HTTPS-only hardening
  (`SECURE_SSL_REDIRECT`, HSTS, secure cookies — see
  [`03-logical-decisions.md`](03-logical-decisions.md) decision 19).

---

## Removed variables

- `CELERY_BROKER_URL` — used by Celery with Redis as the broker. Celery/Redis
  were removed (see [`celery-redis-removal.md`](celery-redis-removal.md)); the
  variable is no longer read. It is safe to delete from your `.env`.
