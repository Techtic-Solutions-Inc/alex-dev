#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_DIR="${ROOT_DIR}/deploy/kubernetes/monitoring"

echo "Validating monitoring manifests with kustomize…"
if command -v kubectl >/dev/null 2>&1; then
  kubectl kustomize "${MONITORING_DIR}" >/dev/null
elif command -v kustomize >/dev/null 2>&1; then
  kustomize build "${MONITORING_DIR}" >/dev/null
else
  echo "kubectl or kustomize is required" >&2
  exit 1
fi

DASHBOARD="${MONITORING_DIR}/grafana-dashboard-backend-api.json"
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import json; json.load(open('${DASHBOARD}'))"
  echo "Grafana dashboard JSON is valid."
else
  echo "python3 not found; skipping dashboard JSON validation."
fi

if command -v promtool >/dev/null 2>&1; then
  TMP_RULES="$(mktemp)"
  kubectl kustomize "${MONITORING_DIR}" >"${TMP_RULES}.yaml"
  echo "PrometheusRule manifest rendered successfully for promtool consumers (${TMP_RULES}.yaml)."
  rm -f "${TMP_RULES}.yaml"
else
  echo "promtool not installed; rule expression syntax was not evaluated."
fi

echo "Monitoring manifest validation completed."