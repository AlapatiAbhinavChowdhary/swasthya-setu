FROM python:3.14-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY src scripts web docs data/diseases.yaml data/sources.yaml ./
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uv", "run", "--frozen", "uvicorn", "swasthya_setu.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
