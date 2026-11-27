# Centralized logging (ELK-compatible)

Ship container stdout JSON to Elasticsearch using Fluent Bit and analyze logs in Kibana.

## Components

| Artifact | Purpose |
| -------- | ------- |
| `fluent-bit-configmap.yaml` | Tail `backend-api` container logs, parse JSON, forward to Elasticsearch |
| `elasticsearch-index-template.json` | Searchable mappings for level, HTTP fields, and request correlation IDs |
| `kibana-dashboard-backend-api-logs.ndjson` | Importable dashboard for log volume and 5xx analysis |

## Setup

1. Create an index template in Elasticsearch:

   ```bash
   curl -X PUT "$ELASTICSEARCH_URL/_index_template/backend-api-logs" \
     -H 'content-type: application/json' \
     --data-binary @deploy/kubernetes/logging/elasticsearch-index-template.json
   ```

2. Deploy the Fluent Bit config (or merge into your cluster-wide Fluent Bit install):

   ```bash
   kubectl apply -k deploy/kubernetes/logging
   ```

3. Import the Kibana dashboard: **Stack Management → Saved Objects → Import** and select `kibana-dashboard-backend-api-logs.ndjson`.

4. Optional direct shipping from the app: set `LOGSTASH_HTTP_URL` to a Logstash HTTP input that writes to Elasticsearch.

See [docs/logging-aggregation.md](../../../docs/logging-aggregation.md) for application-side structured logging fields.