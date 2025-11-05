FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISABLE_PYNPUT=1 \
    HOST=0.0.0.0 \
    PORT=9048

WORKDIR /app

# System deps needed at runtime (curl used by sync)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy the application files
COPY LangFight.py .
COPY encryption_manager.py .
COPY sync_settings.json .
COPY src ./src/

# No extra Python packages are required at build time

EXPOSE 9048

ENTRYPOINT ["python3", "LangFight.py"]
