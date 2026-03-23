# Stage 1: install nanobot-ai + webchat plugin
ARG REGISTRY_PREFIX_DOCKER_HUB=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1 UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install nanobot-ai + this package (registers the webchat entry point)
COPY pyproject.toml .
COPY nanobot_webchat/ ./nanobot_webchat/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache-dir -e .

# Copy workspace (skills, config)
COPY workspace/ ./workspace/
COPY config.json .

# Stage 2: slim runtime
ARG REGISTRY_PREFIX_DOCKER_HUB=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LANG=C.UTF-8

# curl needed for LMS skill (agent uses shell exec)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app
# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

USER nonroot
WORKDIR /app

# nanobot gateway (default port 18790) + webchat ws (8765)
EXPOSE 18790 8765

CMD ["nanobot", "gateway", "--config", "/app/config.json", "--workspace", "/app/workspace"]
