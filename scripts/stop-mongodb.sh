#!/usr/bin/env bash
set -euo pipefail
PID="$(lsof -i :27018 -sTCP:LISTEN -t 2>/dev/null || true)"
if [[ -z "$PID" ]]; then
  echo "No MongoDB process on port 27018"
  exit 0
fi
echo "Stopping MongoDB on port 27018 (pid $PID)"
kill "$PID"
