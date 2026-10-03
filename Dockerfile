# =========================================================
# Stage 1: Build Frontend Static SPA
# =========================================================
FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Enable corepack and install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy monorepo configurations and frontend package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/package.json ./frontend/

# Install frontend dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source code
COPY frontend/ ./frontend/

# Build production bundle to /app/frontend/dist
RUN pnpm --filter frontend run build


# =========================================================
# Stage 2: Production Python Backend + Static Frontend Host
# =========================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Install system runtime & build dependencies for psycopg2 and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend python dependencies and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend codebase and synthetic data
COPY backend/ ./backend/
COPY data/ ./data/

# Copy static frontend assets from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose default HTTP port
EXPOSE 8000

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

# Run database migrations with Alembic and launch Uvicorn server on dynamic PORT
CMD ["sh", "-c", "cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
