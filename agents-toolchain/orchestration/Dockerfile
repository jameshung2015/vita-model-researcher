FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install runtime deps
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6 requests==2.32.3 \
    langchain==0.2.14 langchain-core==0.2.36 pymongo==4.8.0

# Copy code and data needed by governance/loaders
COPY agents-toolchain /app/agents_toolchain
COPY models /app/models
COPY templates /app/templates
COPY benchmarks /app/benchmarks
COPY taxonomy_versions /app/taxonomy_versions
COPY reports /app/reports

# Ensure backward-compatible path for scripts that refer to 'agents-toolchain'
RUN ln -s /app/agents_toolchain /app/agents-toolchain || true

EXPOSE 8080

# Run via package path
CMD ["uvicorn", "agents_toolchain.orchestration.chatbot_api:app", "--host", "0.0.0.0", "--port", "8080"]
