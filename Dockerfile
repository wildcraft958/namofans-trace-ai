FROM python:3.10-slim

WORKDIR /app

# System deps: curl (for rustup), build-essential (for river Rust extensions), nodejs/npm
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (river requires it for compilation)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

# ── Python dependencies ──────────────────────────────────────────────────────
COPY pyproject.toml ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY compliance_rules.yaml ./

# PYTHONPATH must be set before pip install so the editable install's .pth
# does not race with stdlib 'trace' module (Python stdlib has trace.py which
# shadows our package if /app/src isn't prepended to sys.path first).
ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e "."

# ── React frontend ───────────────────────────────────────────────────────────
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci --prefer-offline

COPY frontend/ ./frontend/
RUN cd frontend && npm run build
# dist/ now at /app/frontend/dist — FastAPI serves it via StaticFiles

# ── Demo data (seeded at build time so container starts instantly) ───────────
# Gemini calls are skipped gracefully when no API key is present.
RUN python scripts/seed_demo.py

EXPOSE 8080

CMD ["uvicorn", "trace.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
