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
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## Variable Descriptions

- `SECRET_KEY`  
  Django secret key used for cryptographic signing.

- `DEBUG`  
  Enables debug mode.  
  Should be set to `FALSE` in production.

- `ALLOWED_HOSTS`  
  Comma-separated list of allowed hostnames.

- `CSRF_TRUSTED_ORIGINS`  
  Required for CSRF protection when running behind proxies or Docker.

- `DATABASE_NAME`  
  SQLite database file name (default setup).

- `CELERY_BROKER_URL`  
  Redis URL used by Celery for background task processing.

---

## Notes

- Never commit `.env` files to version control
- Redis must be running for Celery to work
- Production environments should use stronger secrets and a proper database
