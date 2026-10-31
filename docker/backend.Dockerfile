FROM python:3.13.18-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /app
RUN pip install --no-cache-dir uv==0.13.6
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked
COPY backend/app ./app
COPY backend/tests ./tests
EXPOSE 8000
CMD ["uv", "run", "--locked", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--reload"]
