# Backend API

## Getting started

The API reads configuration from environment variables. For local development,
create a `.env` file in the project root before starting the server or running
migrations:

```bash
cp .env.example .env
```

Edit `.env` with your MongoDB connection string, JWT secret, and any optional
integrations (Auth0, SendGrid, APM). NestJS loads `.env` automatically via
`ConfigModule`; at minimum `DATABASE_URL` and `JWT_SECRET` must be set or
startup validation will fail.

```bash
npm ci
npm run start:dev
```

The API listens on `PORT` (default `3000`). OpenAPI is available at
`/api/v1/docs` when the application is running.

Docker and production deployments should inject the same variables (for example
`docker run --env-file .env` or Kubernetes Secrets) rather than relying on a file
committed to the repository.

## Database migrations

MongoDB migrations are versioned TypeScript changes in
`src/database/migrations`. They are executed by a standalone runner rather
than when the Nest application starts. This allows a deployment to migrate the
database before API instances receive traffic.

The runner stores applied versions and immutable checksums in
`_schema_migrations`, and takes an exclusive lock in
`_schema_migration_locks`. A checksum mismatch stops execution: do not alter a
migration that has reached an environment. Create a new migration instead.

### Configuration

Copy `.env.example` and set `MIGRATIONS_DATABASE_URL` to the target MongoDB
database. If it is omitted, the runner uses `DATABASE_URL`. The migration
command reads environment variables supplied by the shell or deployment
platform; for local development, load your `.env` file before invoking it:

```bash
set -a && . ./.env && set +a
```

Use a separate database name for development and test environments. Never run
rollback commands against a production URI without an approved recovery plan.

### Commands

```bash
# Report every known migration and its state
npm run migration:status

# Apply all pending migrations in increasing ID order
npm run migration:up

# Revert the latest applied migration
npm run migration:down

# Revert the latest two migrations
npm run migration:down -- 2

# Compile once, then use the compiled runner (staging/production)
npm run build
npm run migration:status:prod
npm run migration:up:prod
npm run migration:down:prod
```

Migrations are protected against concurrent execution. If a deployment is
interrupted after acquiring the lock, verify that no migration process is
running, investigate the incomplete change, then remove the stale
`_schema_migration_locks` document before retrying. Migrations must therefore
make `up` and `down` safe to retry.

### Writing a migration

Create a lexically increasing file name and register it in
`migration.registry.ts`. Each migration requires an immutable `id`, description,
checksum, and both `up` and `down` functions. `001-initial-schema` creates the
`users` collection, a case-insensitive unique email index, a sparse
verification-token lookup index, and the `app_settings` schema-version seed.
`002-domain-collections` provisions the content, calendar, dashboard, and
profile collections with their compound indexes. Rollbacks remove only indexes
and seed documents; they intentionally never delete application data.

Do not edit a deployed migration, perform unbounded collection scans, or
assume multi-document MongoDB transactions are available. Use idempotent
operations and deploy schema-compatible application code before applying
destructive migrations.

### Tests

The migration suite verifies application ordering, idempotent re-runs,
checksum protection, rollback ordering, and the initial migration's schema
artifacts without contacting a shared database:

```bash
npm run test:migrations
```

## CI/CD

GitHub Actions automates verification on every pull request and deployment from
long-lived branches.

### Continuous integration (`ci.yml`)

Runs on pull requests and pushes to `develop`, `staging`, and `main`:

1. ESLint and Prettier checks
2. Unit tests, migration tests, and e2e tests
3. Production build (`nest build`)

The same workflow is reused as a gate in the CD pipeline via `workflow_call`.

### Continuous delivery (`cd.yml`)

Runs on pushes to environment branches or manual dispatch:

| Branch / input | GitHub Environment |
| -------------- | ------------------ |
| `develop`      | `development`      |
| `staging`      | `staging`          |
| `main`         | `production`       |

Pipeline stages:

1. **Validate** — reuses `ci.yml`
2. **Build image** — multi-stage Docker build pushed to GitHub Container Registry (`ghcr.io/<owner>/<repo>`)
3. **Migrate** — runs `npm run migration:up:prod` against the target database before rollout
4. **Deploy** — updates the runtime via `scripts/deploy.sh` (webhook or Kubernetes)

Manual runs support `skip_deploy` to execute build and migrations only.

### GitHub environment configuration

Create GitHub Environments named `development`, `staging`, and `production`.
Configure secrets per environment:

| Secret / variable | Purpose |
| ----------------- | ------- |
| `MIGRATIONS_DATABASE_URL` | MongoDB URI used by the migration job (preferred) |
| `DATABASE_URL` | Fallback when `MIGRATIONS_DATABASE_URL` is unset |
| `DEPLOY_WEBHOOK_URL` | Optional HTTP hook that receives the image tag and git SHA |
| `KUBE_CONFIG_DATA` | Base64 kubeconfig for Kubernetes rollouts (alternative to webhook) |
| `KUBE_NAMESPACE` (variable) | Target namespace for `kubectl set image` |
| `KUBE_DEPLOYMENT` (variable) | Deployment name to update |

### Container image

```bash
docker build -t backend-api:local .
docker run --rm -p 3000:3000 --env-file .env backend-api:local
```

The image serves the API on port `3000` and exposes a Docker `HEALTHCHECK` on
`/health`.

```bash
npm run docker:smoke
```

## Kubernetes deployment

Manifests live under `deploy/kubernetes` and are rendered with Kustomize.

| Overlay | Namespace | Default replicas |
| ------- | --------- | ---------------- |
| `development` | `backend-api-development` | 1 |
| `staging` | `backend-api-staging` | 2 |
| `production` | `backend-api-production` | 3 |

Resources included:

- **Deployment** — rolling updates, security context, liveness/readiness probes
- **Service (ClusterIP)** — in-cluster service discovery DNS
- **Ingress** — external HTTP load balancing via NGINX
- **HPA** — horizontal pod autoscaling
- **Job** — optional in-cluster database migrations
- **PodDisruptionBudget** (production) — minimum availability during node drains

Validate and deploy:

```bash
npm run kube:validate
bash scripts/kube-deploy.sh production
```

See [deploy/kubernetes/README.md](deploy/kubernetes/README.md) for secret creation,
hostname configuration, and integration with `scripts/deploy.sh`.

## Production error handling and logging

See [docs/logging-aggregation.md](docs/logging-aggregation.md) for ELK/Fluent Bit shipping, correlation IDs, and Kibana dashboards.

In production the API relies on structured Winston logging (`LOG_LEVEL`), the
global HTTP exception filter for consistent client-facing errors
(`success`, `message`, `error.code`, `path`, `timestamp`), and optional APM
export (Datadog/New Relic) for request latency and failures. Uncaught errors are
normalized before they reach clients — never log secrets or raw credentials.
Configure `LOG_LEVEL=info` or `warn` in production, forward container logs to your
aggregator, and alert on elevated `5xx` rates and MongoDB connectivity errors
reported by `GET /api/v1/health`.

## Performance monitoring (APM)

Optional Datadog or New Relic APM integrates at process startup and records HTTP
latency, error rates, slow requests, and runtime health. Configure via `APM_*` and
`DD_*` / `NEW_RELIC_*` variables in `.env.example`.

`GET /api/v1/health` now returns a `system_health` block (uptime, memory, event-loop
delay, APM status) for operational insight.

See [docs/monitoring-alerting.md](docs/monitoring-alerting.md) for Prometheus/Grafana setup and [docs/performance-monitoring.md](docs/performance-monitoring.md) for metrics,
dashboards, and documented bottleneck areas.