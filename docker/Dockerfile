# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

# Create a non-privileged user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy only the installed packages and the app code
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Update PATH to include the user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]