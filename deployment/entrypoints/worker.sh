#!/usr/bin/env bash
set -e

echo "Starting worker..."

python -m workers.run
