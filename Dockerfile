FROM python:3.13-slim@sha256:8f3aba466a471c0ab903dbd7cb979abd4bda370b04789d25440cc90372b50e04

# Define Git SHA build argument for Sentry
ARG git_sha="development"
ENV GIT_SHA=$git_sha

WORKDIR /app

RUN python -m pip install --no-cache-dir -U pip setuptools wheel
RUN python -m pip install --no-cache-dir pdm

COPY pyproject.toml pdm.lock ./
RUN pdm export --prod -o requirements.txt && python -m pip install --no-cache-dir -r requirements.txt

COPY src/ src/
RUN python -m pip install --no-cache-dir .

RUN useradd --no-create-home --shell=/bin/bash reporter
USER reporter

EXPOSE 8000
CMD [ "python", "-m", "uvicorn", "reporter.app:app", "--host", "0.0.0.0" ]
