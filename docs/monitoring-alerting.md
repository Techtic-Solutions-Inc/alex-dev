# Monitoring and alerting

The API exposes Prometheus-compatible metrics and integrates with the existing APM stack (Datadog / New Relic). Cluster operators scrape metrics with Prometheus and visualize them in Grafana.

## Metrics endpoint

| Path | Format | Auth |
| ---- | ------ | ---- |
| `GET /metrics` | Prometheus text exposition 0.0.4 | None (restrict at network / ingress) |

Enable or disable with `METRICS_ENABLED` (default `true` in `staging` and `production`). Prefix metrics with `METRICS_PREFIX` (default `backend_api`).

## Key metrics

| Prometheus name | Type | Description |
| --------------- | ---- | ----------- |
| `backend_api_http_requests_total` | counter | Request volume (`method`, `route`, `status`) |
| `backend_api_http_request_duration_ms_*` | histogram | Latency distribution |
| `backend_api_http_slow_requests_total` | counter | Requests above `APM_SLOW_REQUEST_THRESHOLD_MS` |
| `backend_api_http_server_errors_total` | counter | HTTP 5xx responses |
| `backend_api_application_errors_total` | counter | Logged application errors |
| `backend_api_process_uptime_seconds` | gauge | Process uptime |
| `backend_api_process_heap_used_bytes` | gauge | V8 heap usage |
| `backend_api_process_resident_memory_bytes` | gauge | RSS memory |
| `backend_api_event_loop_delay_ms` | gauge | Mean event-loop lag |

Metrics are populated by `ApmInterceptor` and refreshed on each `/metrics` scrape.

## Prometheus & Grafana

1. Install [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) or an equivalent Prometheus Operator deployment.
2. Apply monitoring manifests: `kubectl apply -k deploy/kubernetes/monitoring`.
3. Import `deploy/kubernetes/monitoring/grafana-dashboard-backend-api.json` into Grafana.
4. Confirm targets show `backend-api` in Prometheus → Status → Targets.

## Alerts

`deploy/kubernetes/monitoring/prometheus-rules.yaml` defines PrometheusRule resources for:

- **BackendApiHighErrorRate** — 5xx ratio above 5% for 10 minutes
- **BackendApiSlowRequestBursts** — frequent slow requests
- **BackendApiHighEventLoopLag** — event-loop delay above 100ms
- **BackendApiHighMemoryUsage** — RSS above 600MB
- **BackendApiMetricsAbsent** — scrape failure / process down

Route alerts through Alertmanager to PagerDuty, Slack, or email.

Validate manifests locally:

```bash
bash scripts/validate-monitoring-manifests.sh
npm run test:unit -- --testPathPattern=prometheus-metrics
npm run test:e2e -- --testPathPattern=metrics.e2e-spec
```

## Vendor APM (optional)

For distributed tracing and vendor dashboards, keep `APM_ENABLED=true` with Datadog or New Relic. See [performance-monitoring.md](./performance-monitoring.md).

## Kubernetes scrape annotations

Pods ship with Prometheus annotations (`prometheus.io/scrape`, `port`, `path`) for legacy annotation-based discovery in addition to the ServiceMonitor.