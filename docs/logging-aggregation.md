# Logging aggregation

The API emits structured JSON logs suitable for the ELK stack (Elasticsearch, Logstash, Kibana) or any log platform that accepts JSON lines.

## Structured fields

Every log line includes:

| Field | Description |
| ----- | ----------- |
| `@timestamp` | Event time (Winston) |
| `level` | `error`, `warn`, `info`, … |
| `message` | Human-readable summary |
| `service.name` / `service.version` | Logical service identity |
| `environment` | Deployment environment |
| `trace.request_id` | Correlation ID (`X-Request-Id` header) |
| `http.*` | Access logs: method, path, status_code, duration_ms |
| `ecs.version` | ECS-compatible metadata marker |

Sensitive values (`password`, `authorization`, `token`, `secret`, …) are redacted to `[REDACTED]` before emission.

## Application configuration

| Variable | Description |
| -------- | ----------- |
| `LOG_LEVEL` | Minimum log level (`info` in production) |
| `LOG_SERVICE_NAME` | `service.name` label (defaults to `DD_SERVICE` or `backend-api`) |
| `DD_ENV` / `NODE_ENV` | `environment` field |
| `LOGSTASH_ENABLED` | Enable HTTP log shipping |
| `LOGSTASH_HTTP_URL` | Logstash HTTP input or compatible NDJSON endpoint |
| `LOGSTASH_BATCH_SIZE` | Batch size before async flush (default `25`) |
| `LOGSTASH_FLUSH_INTERVAL_MS` | Periodic flush interval (default `2000`) |

When `LOGSTASH_HTTP_URL` is unset, logs are written to stdout only. Kubernetes collectors (Fluent Bit / Filebeat) forward stdout to Elasticsearch.

## Correlation IDs

`RequestContextMiddleware` assigns or propagates `X-Request-Id`. Clients may supply their own value; otherwise the API generates a UUID. Access logs include `trace.request_id` for cross-service search in Kibana:

```
trace.request_id: "client-trace-001"
```

## Dashboards & search examples

Import `deploy/kubernetes/logging/kibana-dashboard-backend-api-logs.ndjson`.

Useful Kibana queries:

- Errors: `level: "error"`
- Client failures: `http.status_code >= 400`
- Slow requests: `http.duration_ms > 2000`
- By route: `http.path: "/api/v1/auth/login"`

## Verification

```bash
npm run test:unit -- --testPathPattern=structured-log
npm run test:e2e -- --testPathPattern=structured-logging
bash scripts/validate-logging-manifests.sh
```

Ensure container logs show JSON with `service.name` before promoting to production.