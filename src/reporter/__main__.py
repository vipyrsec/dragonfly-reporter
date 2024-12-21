"""Reports malicious packages to PyPI."""

import uvicorn

from reporter.app import app

uvicorn.run(app)
