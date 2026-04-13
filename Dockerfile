# LunVex Code Docker Image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash lunvex
WORKDIR /home/lunvex/app
RUN chown -R lunvex:lunvex /home/lunvex

# Switch to non-root user
USER lunvex

# Create virtual environment
RUN python -m venv /home/lunvex/venv
ENV PATH="/home/lunvex/venv/bin:$PATH"

# Copy requirements first for better caching
COPY --chown=lunvex:lunvex requirements.txt .
COPY --chown=lunvex:lunvex pyproject.toml .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Copy application code
COPY --chown=lunvex:lunvex . .

# Create necessary directories
RUN mkdir -p /home/lunvex/.lunvex-code

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (interactive mode)
CMD ["lunvex-code", "run"]

# Labels
LABEL org.opencontainers.image.title="LunVex Code" \
      org.opencontainers.image.description="Terminal AI coding assistant for real projects" \
      org.opencontainers.image.url="https://github.com/artemmelnik/lunvex-code" \
      org.opencontainers.image.source="https://github.com/artemmelnik/lunvex-code" \
      org.opencontainers.image.licenses="MIT"
