FROM python:3.14.4-slim-bookworm

RUN  --mount=type=cache,target=/var/cache/apt,id=global_apt_cache,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,id=global_apt_lists,sharing=locked \
    apt-get update && \
    apt-get  -y -o Dir::Cache::Archives=/var/cache/apt/ install \
    --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    postgresql-client

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_DIR=/app \
    USER=app \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

ARG UID=1000
ARG GID=1000


RUN groupadd -g $GID -o ${USER}
RUN useradd -ms /bin/bash -u $UID -g $GID ${USER}

USER ${USER}
WORKDIR ${PROJECT_DIR}

COPY --chown=${UID}:${GID} pyproject.toml uv.lock ./
 
# Use docker buildkit's caching to use caching of uv download packages
RUN --mount=type=cache,target=/home/${USER}/.cache/uv,id=uv-cache,uid=${UID},gid=${GID} \
    uv sync --dev
 
ADD --chown=${UID}:${GID} . /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"