#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERLAYS=(
  development
  staging
  production
)

render_kustomize() {
  local target="$1"
  if command -v kubectl >/dev/null 2>&1; then
    kubectl kustomize "${target}"
    return
  fi
  if command -v kustomize >/dev/null 2>&1; then
    kustomize build "${target}"
    return
  fi
  echo "kubectl or kustomize is required to validate Kubernetes manifests." >&2
  exit 1
}

for overlay in "${OVERLAYS[@]}"; do
  target="${ROOT_DIR}/deploy/kubernetes/overlays/${overlay}"
  echo "Rendering overlay: ${overlay}"
  render_kustomize "${target}" >/dev/null
done

echo "Kubernetes manifest validation succeeded for all overlays."