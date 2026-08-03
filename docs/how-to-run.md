# How to Run
This document explains how to run the project locally for development or testing.
You can either use Docker (recommended) or run it directly using Django.

---

## Option 1: Run Using Docker (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd it-club-website
   ```

2. Create the environment file:
   ```bash
   cp example.env .env
   ```

3. Update the `.env` file as needed.
   Refer to `docs/environment-variables.md` for details.

4. Build and start the containers:
   ```bash
   docker compose up --build
   ```

5. The `entrypoint.sh` script will automatically:
   - Collect static files (only when `DEBUG` is not `true`)
   - Run database migrations
   - Seed initial data (if configured)
   - Start the application using Gunicorn (or `runserver` when `DEBUG=TRUE`)

   The image runs as UID `1000`. In dev, `docker-compose.override.yml`
   additionally bind-mounts the repo over `/app` for hot-reload; on Linux make
   sure the host UID owns the repo so `media/` and `db.sqlite3` stay writable.

6. Open the application:
   ```
   http://localhost:8000
   ```

---

## Option 2: Run Without Docker (Local Development)

### Prerequisites
- Python 3.14
- pip

Virtual environments (venv, virtualenv, Conda/Miniforge) are optional but recommended.

---

### Setup Steps

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create the environment file:
   ```bash
   cp example.env .env
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Admin Panel

- URL:
  ```
  /admin
  ```
- Login using the superuser credentials.

---

## Notes

- SQLite is used by default.
- Docker is the preferred setup for consistency.
- The project is in early development; steps may evolve.

