# ═══════════════════════════════════════════════════════════════════════════
# Dockerfile for QiskitCommunitySolver Organism
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="DNALang Framework"
LABEL description="Autopoietic organism for Qiskit community support"
LABEL version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy organism files
COPY organisms/ ./organisms/
COPY runtime/ ./runtime/
COPY docs/ ./docs/
COPY README.md .

# Create data directory for organism state
RUN mkdir -p /app/organism_data && \
    chmod 755 /app/organism_data

# Create non-root user for security
RUN useradd -m -u 1000 organism && \
    chown -R organism:organism /app

USER organism

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Environment variables (can be overridden)
ENV ORGANISM_LOG_LEVEL=INFO
ENV ORGANISM_LOOP_INTERVAL=3600
ENV ORGANISM_PORT=8000
ENV PYTHONUNBUFFERED=1

# Run organism in both modes (autonomous + web service)
CMD ["python", "runtime/aura_bot.py", \
     "--mode", "both", \
     "--port", "8000", \
     "--log-level", "INFO", \
     "--loop-interval", "3600"]
