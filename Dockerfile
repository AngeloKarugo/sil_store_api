# Lightweight Dockerfile for the Django app
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . /app

ENV PORT 8010
EXPOSE ${PORT}

CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8010", "--workers", "3"]
