# Prometheus / Grafana monitoring

Apply these manifests after the Prometheus Operator (kube-prometheus-stack) is installed in your cluster.

```bash
kubectl apply -k deploy/kubernetes/monitoring
```

## Components

| File | Purpose |
| ---- | ------- |
| `servicemonitor.yaml` | Scrapes `GET /metrics` every 30s from the backend Service |
| `prometheus-rules.yaml` | Alert rules for error rate, slow requests, memory, event-loop lag, scrape loss |
| `grafana-dashboard-backend-api.json` | Import into Grafana (Dashboards → Import) |

Adjust `namespaceSelector` in the ServiceMonitor to match your deployment namespace.

## Alert validation

```bash
bash scripts/validate-monitoring-manifests.sh
```