FROM python:3.11-slim@sha256:6459da0f052d819e59b5329bb8f76b2f2bd16427ce6fd4db91e11b3759850380 as builder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

WORKDIR /app
COPY README.md pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm sync --prod --no-editable
COPY src/ src/
RUN pdm sync --prod --no-editable


FROM builder as test

RUN pdm install -d
COPY tests/ tests/
CMD ["pdm", "run", "pytest"]


FROM python:3.11-slim@sha256:6459da0f052d819e59b5329bb8f76b2f2bd16427ce6fd4db91e11b3759850380 as prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app

COPY --from=builder /app/__pypackages__/3.11/lib pkgs/

COPY src/ src/

CMD ["python", "-m", "uvicorn", "reporter.app:app", "--host", "0.0.0.0"]

EXPOSE 8000
