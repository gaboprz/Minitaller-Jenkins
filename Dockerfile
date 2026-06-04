FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

FROM base AS ci-base

COPY .flake8 ./
COPY requirements-dev.txt ./
COPY buscaminas.py ./
COPY tests ./tests
RUN pip install --no-cache-dir -r requirements-dev.txt

FROM ci-base AS lint

CMD ["flake8", "."]

FROM base AS unit-test

COPY requirements-dev.txt ./
COPY tests ./tests
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["pytest", "tests/test_domain.py", "tests/test_ranking.py", "--junitxml=reports/unit-tests.xml"]

FROM base AS develop

COPY Datos ./Datos
COPY buscaminas.py ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk \
    && rm -rf /var/lib/apt/lists/*
CMD ["python", "buscaminas.py"]
