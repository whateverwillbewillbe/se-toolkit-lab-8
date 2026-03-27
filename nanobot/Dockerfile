# Nanobot gateway Dockerfile
# Multi-stage build with uv

ARG REGISTRY_PREFIX_DOCKER_HUB

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root files for dependency resolution
COPY --from=workspace pyproject.toml uv.lock /app/
COPY pyproject.toml /app/nanobot/pyproject.toml

# Sync the nanobot package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# Copy the nanobot application
COPY . /app/nanobot

# Copy mcp directory for lms-mcp dependency
COPY --from=workspace mcp /app/mcp

# Copy packages/nanobot-ai for nanobot-ai dependency
COPY --from=workspace packages/nanobot-ai /app/packages/nanobot-ai

# Copy nanobot-websocket-channel for webchat channel
COPY --from=workspace nanobot-websocket-channel /app/nanobot-websocket-channel

# Sync again with the full package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# ---
# Stage 2: Final runtime image
# ---
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

USER nonroot

WORKDIR /app/nanobot

# Run the entrypoint which resolves config and launches gateway
CMD ["python", "/app/nanobot/entrypoint.py"]
