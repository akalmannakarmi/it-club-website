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
   - Run database migrations
   - Collect static files
   - Seed initial data (if configured)
   - Start the application using Gunicorn

6. Open the application:
   ```
   http://localhost:8000
   ```

---

## Option 2: Run Without Docker (Local Development)

### Prerequisites
- Python 3.14
- pip
- Redis (for Celery)

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

6. (Optional) Start Celery worker in another terminal:
   ```bash
   celery -A config worker -l info

7. (Optional) Start Celery beat in another terminal:
   ```bash
   celery -A config beat -l info
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

