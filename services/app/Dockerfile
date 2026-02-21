FROM python:3.11-slim AS builder
WORKDIR /build
COPY services/app/pyproject.toml ./pyproject.toml
RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels .

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY services/app/app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
