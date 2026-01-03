#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Starting server"
source "$PROJECT_DIR/venv/bin/activate"
python "$PROJECT_DIR/server.py" &
SERVER_PID=$!

cleanup() {
	echo "Stopping server"
	kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for server to start..."
until curl -s http://localhost:5000/ >/dev/null 2>&1; do
	sleep 0.2
done

echo "Server started."
xdg-open "http://localhost:5000/" >/dev/null 2>&1

wait "$SERVER_PID"