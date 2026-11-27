#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-}"

if [ -z "${ENVIRONMENT}" ]; then
  echo "Usage: kube-deploy.sh <development|staging|production>" >&2
  exit 1
fi

case "${ENVIRONMENT}" in
  development | staging | production) ;;
  *)
    echo "Unsupported environment: ${ENVIRONMENT}" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERLAY="${ROOT_DIR}/deploy/kubernetes/overlays/${ENVIRONMENT}"
NAMESPACE="backend-api-${ENVIRONMENT}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required." >&2
  exit 1
fi

kubectl apply -k "${OVERLAY}"
kubectl -n "${NAMESPACE}" rollout status deployment/backend-api --timeout=300s
kubectl -n "${NAMESPACE}" get ingress,svc,hpa

echo "Kubernetes deployment completed for ${ENVIRONMENT}."