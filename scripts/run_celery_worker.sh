#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source venv/bin/activate
# --pool=solo: required on Python 3.13+ (prefork/billiard _localized bug on macOS)
celery -A app.core.celery_app worker --loglevel=info --pool=solo
