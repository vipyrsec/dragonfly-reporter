# syntax=docker/dockerfile:latest
# hadolint global shell=bash

# DEBIAN_VERSION The version of Debian to use for the base image
ARG DEBIAN_VERSION=bookworm
# DEBIAN_FRONTEND The frontend of the Apt package manager to use
ARG DEBIAN_FRONTEND=noninteractive
# PYTHON_VERSION The version of Python to use for the base image
ARG PYTHON_VERSION=3.12

# build builds the virtual environment of the project
FROM python:$PYTHON_VERSION-slim-$DEBIAN_VERSION AS build
ARG DEBIAN_FRONTEND
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
SHELL ["/bin/bash", "-c"]

COPY --link --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/

WORKDIR /opt

# hadolint ignore=DL4006
RUN --mount=type=cache,target=/root/.cache/uv \
  <<EOT
#!/usr/bin/env bash
set -e

apt-get -q update
apt-get -qy upgrade
apt-get -qy install --no-install-recommends git
EOT

COPY --link pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-install-project --no-default-groups

COPY --link src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install .

# release uses the built virtual environment of the project
FROM python:$PYTHON_VERSION-slim-$DEBIAN_VERSION AS release
ARG DEBIAN_FRONTEND
SHELL ["/bin/bash", "-c"]

# Define Git SHA build argument for sentry
ARG GIT_SHA="development"
ENV GIT_SHA=$GIT_SHA

WORKDIR /app
COPY --link --from=build /opt/.venv /opt/.venv

# hadolint ignore=DL4006
RUN --mount=type=cache,target=/root/.cache/pip \
  <<EOT
#!/usr/bin/env bash
set -e

apt-get -q update
apt-get -qy upgrade

python3 -m pip install --no-cache-dir --use-pep517 --check-build-dependencies -U pip setuptools wheel build

apt-get -qy clean
rm -rf /var/lib/apt/lists/*

useradd --no-create-home --shell=/bin/bash reporter
EOT

ENV PATH="/opt/.venv/bin:${PATH}"

COPY --link LICENSE entrypoint.sh ./

USER reporter

CMD ["/app/entrypoint.sh"]
