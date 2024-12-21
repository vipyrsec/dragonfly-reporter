FROM python:3.12-slim@sha256:2b0079146a74e23bf4ae8f6a28e1b484c6292f6fb904cbb51825b4a19812fcd8

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
