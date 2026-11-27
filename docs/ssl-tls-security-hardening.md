# SSL/TLS and security hardening

This service terminates TLS at the ingress in Kubernetes and can serve HTTPS directly when certificate paths are configured for local or bare-metal deployments.

## TLS certificate acquisition

### Kubernetes (recommended)

1. Install [cert-manager](https://cert-manager.io/) in the cluster.
2. Create a `ClusterIssuer` for Let's Encrypt (staging for non-production, production issuer in the production overlay).
3. Apply the base manifests. The `Certificate` resource (`deploy/kubernetes/base/certificate.yaml`) requests a certificate for `api.example.com` and stores it in the `backend-api-tls` secret consumed by the `Ingress` TLS block.
4. The production overlay sets `cert-manager.io/cluster-issuer: letsencrypt-prod` on the ingress.

### Local development

Generate a self-signed certificate:

```bash
bash scripts/generate-dev-tls.sh
export SSL_CERT_PATH=deploy/tls/dev/server.crt
export SSL_KEY_PATH=deploy/tls/dev/server.key
export TLS_ENABLED=true
npm run start
```

## Application HTTPS configuration

| Variable | Description |
| -------- | ----------- |
| `TLS_ENABLED` | Set to `true` to enable HTTPS when cert paths are present. |
| `SSL_CERT_PATH` | PEM certificate file path. |
| `SSL_KEY_PATH` | PEM private key file path. |
| `SSL_CA_PATH` | Optional CA bundle for mutual TLS clients. |
| `TRUST_PROXY` | When `true`, Express trusts `X-Forwarded-*` headers (default in production/staging). |
| `FORCE_HTTPS` | When `true`, requests with `X-Forwarded-Proto: http` receive an HTTP 301 redirect to HTTPS. |
| `SECURITY_HSTS_ENABLED` | Emit `Strict-Transport-Security` from the Node process (ingress also sends HSTS). |
| `SECURITY_HSTS_MAX_AGE_SECONDS` | HSTS max-age when enabled (default `31536000`). |

Behind nginx ingress the pod typically listens on HTTP port 3000; TLS is handled at the edge.

## Hardening measures

- **HTTP headers** — `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Resource-Policy`, `Cross-Origin-Opener-Policy`, and a restrictive `Content-Security-Policy` are applied to every response (`security-headers.bootstrap.ts`).
- **`X-Powered-By` disabled** — reduces fingerprinting.
- **Ingress** — forced SSL redirect, HSTS (1 year, subdomains, preload), and supplemental security headers via nginx annotations.
- **Pod security** — non-root user, read-only root filesystem, dropped capabilities, seccomp `RuntimeDefault`, and no automounted service account token (see `deployment.yaml`).
- **Rate limiting** — existing middleware remains enabled.

## Vulnerability verification

Automated checks:

```bash
npm run test:unit -- --testPathPattern=security.config.spec.ts
npm run test:e2e -- --testPathPattern=security-headers
```

Manual checks (with the API running):

- Confirm responses include hardened headers (`curl -sI https://api.example.com/api/v1/health`).
- Confirm HTTP clients are redirected to HTTPS at the ingress.
- Run OWASP ZAP or `nuclei` against staging before production promotion.

Report security issues through your organisation's vulnerability management process; do not expose stack traces or internal identifiers in API error payloads.