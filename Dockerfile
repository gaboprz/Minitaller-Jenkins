FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

FROM base AS unit-test

COPY tests ./tests
CMD ["python", "-m", "unittest", "discover", "-s", "tests"]

FROM base AS develop

COPY Datos ./Datos
COPY buscaminas.py ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk \
    && rm -rf /var/lib/apt/lists/*
CMD ["python", "buscaminas.py"]
