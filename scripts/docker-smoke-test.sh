#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_TAG="${1:-backend-api:local}"
CONTAINER_NAME="backend-api-smoke-$$"
PORT="${SMOKE_TEST_PORT:-3100}"

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Building image ${IMAGE_TAG}..."
docker build -t "${IMAGE_TAG}" "${ROOT_DIR}"

echo "Starting container on port ${PORT}..."
docker run -d --name "${CONTAINER_NAME}" \
  -e NODE_ENV=production \
  -e PORT=3000 \
  -e JWT_SECRET=smoke-test-jwt-secret-at-least-32-characters \
  -e DATABASE_URL=mongodb://127.0.0.1:27017/smoke \
  -p "${PORT}:3000" \
  "${IMAGE_TAG}" >/dev/null

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null; then
    echo "Docker smoke test passed: GET /health returned 200."
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for ${IMAGE_TAG} to become healthy." >&2
docker logs "${CONTAINER_NAME}" >&2 || true
exit 1