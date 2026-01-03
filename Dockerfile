FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Optional build tools
# RUN apt-get update \
#    && apt-get install -y --no-install-recommends build-essential \
#    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make /app writable for UID 1000
RUN chown -R 1000:1000 /app

# Switch to UID 1000
USER 1000:1000

CMD ["bash", "entrypoint.sh"]

