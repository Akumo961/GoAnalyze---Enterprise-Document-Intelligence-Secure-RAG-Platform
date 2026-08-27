FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system --gid 65532 appgroup \
    && useradd --system --no-create-home --uid 65532 --gid 65532 appuser

COPY pyproject.toml /app/
COPY gov_platform /app/gov_platform
COPY alembic.ini /app/
COPY migrations /app/migrations

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc librdkafka-dev \
    && pip install . \
    && apt-get purge -y --auto-remove gcc librdkafka-dev \
    && rm -rf /var/lib/apt/lists/* /root/.cache /tmp/*

USER 65532:65532

EXPOSE 8080

CMD ["uvicorn", "gov_platform.main:app", "--host", "0.0.0.0", "--port", "8080"]
