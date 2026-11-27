# Performance monitoring and APM

The API ships with optional Application Performance Monitoring (APM) that records
request latency, error rates, runtime resource usage, and event-loop health.

## Providers

| Provider | Enable | Required secrets / env |
| -------- | ------ | ---------------------- |
| **Datadog** (default) | `APM_ENABLED=true`, `APM_PROVIDER=datadog` | Datadog agent reachable via `DD_AGENT_HOST` |
| **New Relic** | `APM_ENABLED=true`, `APM_PROVIDER=newrelic` | `NEW_RELIC_LICENSE_KEY` |

Shared settings:

- `DD_SERVICE` / `NEW_RELIC_APP_NAME` — logical service name
- `DD_ENV` — deployment environment label
- `DD_VERSION` — release version (image tag or git SHA)
- `APM_SLOW_REQUEST_THRESHOLD_MS` — slow-request alert threshold (default `2000`)

## Metrics emitted

| Metric | Type | Purpose |
| ------ | ---- | ------- |
| `api.http.requests` | counter | Request volume by method, route, status |
| `api.http.request.duration_ms` | histogram | Latency distribution for user experience |
| `api.http.slow_requests` | counter | Requests above the slow threshold |
| `api.errors` | counter | Server-side error events |

Datadog also enables **runtime metrics** (CPU, memory, GC) and automatic HTTP/Express
instrumentation when the agent is connected.

## Runtime health surface

`GET /api/v1/health` includes a `system_health` object:

- `uptime_seconds`
- `memory_heap_used_mb` / `memory_rss_mb`
- `event_loop_delay_ms` (event-loop lag indicator)
- `apm_enabled` / `apm_provider`

Use this for quick dashboards and synthetic checks; use the APM vendor UI for
deeper traces and historical trends.

## Known bottlenecks to watch

| Area | Symptom in APM | Mitigation |
| ---- | -------------- | ---------- |
| MongoDB | High duration on health, auth, list endpoints | Confirm indexes from migrations; scale cluster; tune pool timeouts |
| Auth0 login | Spikes on `POST /auth/login` | External dependency latency; monitor error rate and timeouts |
| SendGrid email | Slow signup path | Async retries; verify outbound network from cluster |
| Rate limiter middleware | Uniform latency on all routes | Tune `RATE_LIMIT_POINTS`; scale replicas for higher ingress |
| Large list queries | Slow `GET` content/profile endpoints | Enforce pagination limits; index-backed filters |
| Event loop lag | Rising `event_loop_delay_ms` in health | Scale pods; profile CPU-heavy work; avoid sync blocking |

## Kubernetes notes

- Set `DD_AGENT_HOST` from the downward API (`status.hostIP`) when using the
  Datadog DaemonSet agent.
- Enable `APM_ENABLED=true` in production overlays after secrets are configured.
- Pair APM with existing HPA metrics (CPU/memory) to validate scaling decisions.