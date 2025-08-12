FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

# System dependencies (added postgresql-client for proper health checks)
RUN apt-get update && \
    apt-get install -y \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY alembic.ini .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]