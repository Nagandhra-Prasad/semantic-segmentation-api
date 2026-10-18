#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p data/mongodb

if command -v mongod >/dev/null 2>&1; then
  MONGOD="$(command -v mongod)"
elif [[ -x /opt/homebrew/opt/mongodb-community@7.0/bin/mongod ]]; then
  MONGOD="/opt/homebrew/opt/mongodb-community@7.0/bin/mongod"
else
  echo "mongod not found. Install: brew install mongodb-community@7.0"
  exit 1
fi

if lsof -i :27018 -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "MongoDB already listening on port 27018"
  exit 0
fi

echo "Starting MongoDB for semantic-segmentation-api on mongodb://localhost:27018"
exec "$MONGOD" --config config/mongod-semantic-segmentation.conf
