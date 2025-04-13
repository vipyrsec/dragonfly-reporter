#!/usr/bin/env bash
set -eu

RELOAD=""
if [ "$GIT_SHA" = "development" ] || [ "$GIT_SHA" = "testing" ]; then
	RELOAD=--reload
fi

uvicorn reporter.app:app --host 0.0.0.0 $RELOAD

exec $0
