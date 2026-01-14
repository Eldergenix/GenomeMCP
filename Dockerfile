# Use Python 3.12 to satisfy denario/research dependencies if needed
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies (including optional ones if desired, or just core)
# We install core + uvicorn. Note: --system installs into site-packages, avoiding venv complexity in Docker
# We skip 'research' group to avoid complex heavy deps unless requested, 
# but if pyproject requires it for resolution, we might need it.
# using --no-dev to keep image small.
RUN uv pip install --system .[llm] uvicorn supervisor

# Copy source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
