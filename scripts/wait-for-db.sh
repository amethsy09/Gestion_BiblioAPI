#!/bin/sh
set -e

DB_HOST=${DATABASE_HOST:-db}
DB_PORT=${DATABASE_PORT:-5432}
MAX_RETRIES=${MAX_RETRIES:-20}
SLEEP=${SLEEP:-3}

echo "Waiting for DB ${DB_HOST}:${DB_PORT}..."
for i in $(seq 1 $MAX_RETRIES); do
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
    echo "DB ready"
    exit 0
  fi
  echo "Attempt $i/$MAX_RETRIES - waiting ${SLEEP}s..."
  sleep $SLEEP
done

echo "DB not ready after ${MAX_RETRIES} attempts" >&2
exit 1
