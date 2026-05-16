FROM python:3.10-slim

WORKDIR /app

# System deps: curl (for rustup) + build-essential (for river Rust extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (river requires it for compilation)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency manifest first (better layer caching)
COPY pyproject.toml ./

# Copy application source
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY compliance_rules.yaml ./

# Install Python package (sources cargo env automatically via PATH above)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e "."

# Pre-seed demo data at build time.
# seed_demo.py gracefully skips Gemini calls when the API key is absent,
# so this step succeeds even without GOOGLE_API_KEY in the build environment.
RUN python scripts/seed_demo.py

EXPOSE 8080

CMD ["uvicorn", "trace.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
