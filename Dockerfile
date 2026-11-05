
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.5.1

# Install Python dependencies
COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

# Copy application
COPY src ./src
COPY alembic.ini ./

# Prepare application directory
RUN useradd --create-home --shell /usr/sbin/nologin app && \
    touch logs.log && \
    chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
