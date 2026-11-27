#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/deploy/tls/dev"
DAYS="${TLS_CERT_DAYS:-825}"
COMMON_NAME="${TLS_COMMON_NAME:-localhost}"

mkdir -p "${OUT_DIR}"

openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -sha256 \
  -days "${DAYS}" \
  -subj "/CN=${COMMON_NAME}" \
  -keyout "${OUT_DIR}/server.key" \
  -out "${OUT_DIR}/server.crt"

chmod 600 "${OUT_DIR}/server.key"
chmod 644 "${OUT_DIR}/server.crt"

cat <<EOF
Development TLS material written to:
  SSL_CERT_PATH=${OUT_DIR}/server.crt
  SSL_KEY_PATH=${OUT_DIR}/server.key

Start the API with HTTPS enabled:
  export SSL_CERT_PATH=${OUT_DIR}/server.crt
  export SSL_KEY_PATH=${OUT_DIR}/server.key
  export TLS_ENABLED=true
  npm run start
EOF