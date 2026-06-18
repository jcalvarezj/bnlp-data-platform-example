FROM apache/airflow:3.2.2

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

USER root

RUN uv pip compile pyproject.toml -o requirements.txt \
    && uv pip install -r requirements.txt --system

USER airflow
