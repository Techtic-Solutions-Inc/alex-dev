#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGGING_DIR="${ROOT_DIR}/deploy/kubernetes/logging"

echo "Validating logging manifests…"
if command -v kubectl >/dev/null 2>&1; then
  kubectl kustomize "${LOGGING_DIR}" >/dev/null
elif command -v kustomize >/dev/null 2>&1; then
  kustomize build "${LOGGING_DIR}" >/dev/null
else
  echo "kubectl or kustomize is required" >&2
  exit 1
fi

TEMPLATE="${LOGGING_DIR}/elasticsearch-index-template.json"
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import json; json.load(open('${TEMPLATE}'))"
  python3 -c "import json; json.load(open('${LOGGING_DIR}/kibana-dashboard-backend-api-logs.ndjson'))"
  echo "Elasticsearch template and Kibana export JSON are valid."
fi

echo "Logging manifest validation completed."