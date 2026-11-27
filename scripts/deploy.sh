#!/usr/bin/env bash
set -euo pipefail

require_var() {
  local name="$1"
  if [ -z "${!name:-}" ]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 1
  fi
}

require_var DEPLOY_ENVIRONMENT
require_var DEPLOY_IMAGE

payload() {
  cat <<EOF
{
  "environment": "${DEPLOY_ENVIRONMENT}",
  "image": "${DEPLOY_IMAGE}",
  "imageLatest": "${DEPLOY_IMAGE_LATEST:-}",
  "gitSha": "${DEPLOY_REF:-}",
  "triggeredBy": "${DEPLOY_ACTOR:-github-actions}"
}
EOF
}

deploy_with_webhook() {
  echo "Deploying ${DEPLOY_IMAGE} to ${DEPLOY_ENVIRONMENT} via webhook."
  curl --fail-with-body --silent --show-error \
    -X POST "${DEPLOY_WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
  -d "$(payload)"
}

deploy_with_kubernetes() {
  require_var KUBE_NAMESPACE
  require_var KUBE_DEPLOYMENT

  if ! command -v kubectl >/dev/null 2>&1; then
    echo "kubectl is required for Kubernetes deployments." >&2
    exit 1
  fi

  local kubeconfig="${RUNNER_TEMP}/kubeconfig"
  echo "${KUBE_CONFIG_DATA}" | base64 -d > "${kubeconfig}"
  export KUBECONFIG="${kubeconfig}"

  local container_name="${KUBE_CONTAINER:-backend-api}"
  echo "Updating deployment/${KUBE_DEPLOYMENT} in namespace ${KUBE_NAMESPACE}."
  kubectl -n "${KUBE_NAMESPACE}" set image "deployment/${KUBE_DEPLOYMENT}" \
    "${container_name}=${DEPLOY_IMAGE}"
  kubectl -n "${KUBE_NAMESPACE}" rollout status "deployment/${KUBE_DEPLOYMENT}" --timeout=180s
}

if [ -n "${DEPLOY_WEBHOOK_URL:-}" ]; then
  deploy_with_webhook
elif [ -n "${KUBE_CONFIG_DATA:-}" ]; then
  deploy_with_kubernetes
else
  echo "No deployment integration configured for ${DEPLOY_ENVIRONMENT}." >&2
  echo "Set DEPLOY_WEBHOOK_URL or KUBE_CONFIG_DATA on the GitHub environment." >&2
  exit 1
fi

echo "Deployment completed for ${DEPLOY_ENVIRONMENT}."