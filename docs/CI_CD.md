# CI/CD Pipeline

This project uses [GitHub Actions](https://docs.github.com/en/actions) to automate linting, testing, Docker image builds, and deployment to **Amazon Web Services (AWS)** via **Elastic Container Registry (ECR)** and **Elastic Container Service (ECS)**.

Workflow definition: [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml)

## Pipeline overview

```mermaid
flowchart LR
    A[Push / PR] --> B[Lint]
    B --> C[Test]
    C --> D[Build Docker]
    D --> E{Branch push?}
    E -->|main or develop| F[Publish to ECR]
    E -->|PR| G[Stop]
    F --> H{main only?}
    H -->|yes| I[Deploy to ECS]
    H -->|no| G
```

| Job | Purpose | Runs on |
| --- | --- | --- |
| **Lint** | `black --check` and `flake8` | Every push and pull request |
| **Test** | `pytest` against PostgreSQL 16 | Every push and pull request |
| **Build Docker** | Builds the image and runs a container smoke test | Every push and pull request |
| **Publish Image** | Pushes the image to Amazon ECR | Push to `main` or `develop` only |
| **Deploy** | Updates the ECS service with the new task definition | Push to `main` only |

## Triggers

- **Pull requests** targeting `main` or `develop`: lint, test, and Docker build (no publish/deploy).
- **Pushes** to `main` or `develop`: lint, test, build, and publish to ECR.
- **Pushes** to `main`: additionally deploy to ECS production.
- **Manual runs**: use **Actions → CI/CD Pipeline → Run workflow** (`workflow_dispatch`).

## Prerequisites

### AWS resources

1. **ECR repository** (for example `fastapi-backend`).
2. **ECS Fargate cluster** and service running the application.
3. **CloudWatch log group** `/ecs/fastapi-backend` (or update the task definition).
4. **Secrets Manager** entries for runtime secrets (`DATABASE_URL`, `JWT_SECRET`, etc.).
5. **IAM roles**:
   - `ecsTaskExecutionRole` — pull images and read secrets.
   - `ecsTaskRole` — application permissions at runtime.
   - GitHub Actions deploy role (OIDC recommended) — push to ECR and update ECS.

### GitHub configuration

Configure the following in **Settings → Secrets and variables → Actions**.

#### Secrets

| Secret | Required | Description |
| --- | --- | --- |
| `AWS_ROLE_ARN` | Recommended | IAM role ARN for OIDC-based authentication (preferred). |
| `AWS_ACCESS_KEY_ID` | Alternative | Access key when OIDC is not configured. |
| `AWS_SECRET_ACCESS_KEY` | Alternative | Secret key when OIDC is not configured. |

Use **either** OIDC (`AWS_ROLE_ARN`) **or** static access keys — not both unless your org requires it.

#### Variables

| Variable | Default | Description |
| --- | --- | --- |
| `AWS_REGION` | `us-east-1` | AWS region for ECR and ECS. |
| `ECR_REPOSITORY` | `fastapi-backend` | ECR repository name. |
| `ECS_CLUSTER` | — | Target ECS cluster name (required for deploy). |
| `ECS_SERVICE` | — | Target ECS service name (required for deploy). |

#### GitHub environment

Create a **`production`** environment (Settings → Environments) for the deploy job. Add required reviewers or protection rules as needed.

## AWS OIDC setup (recommended)

1. Create an IAM OIDC identity provider for `token.actions.githubusercontent.com`.
2. Create an IAM role with a trust policy scoped to this repository:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:ORG/REPO:*"
        }
      }
    }
  ]
}
```

3. Attach policies allowing ECR push and ECS service updates.
4. Store the role ARN in `AWS_ROLE_ARN`.

## ECS task definition

Template: [`deploy/ecs-task-definition.json`](../deploy/ecs-task-definition.json)

Before first deploy, replace placeholders:

- `ACCOUNT_ID` — your AWS account ID.
- `REGION` — your AWS region.
- IAM role ARNs and Secrets Manager ARNs.

The pipeline renders the container image URI automatically during deployment.

## Local Docker usage

Build and run the application locally:

```bash
docker build -t fastapi-backend:local .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:password@host.docker.internal:5432/dbname \
  -e JWT_SECRET=local-dev-secret \
  -e ENVIRONMENT=development \
  fastapi-backend:local
```

Verify health:

```bash
curl http://localhost:8000/health
```

## Running CI steps locally

```bash
# Lint
black --check main.py src/
flake8 .

# Tests (requires PostgreSQL matching DATABASE_URL / DATABASE_URL_TEST)
pytest src/tests -v
```

Environment variables used in CI are documented at the top of [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml).

## Deployment behavior

1. A push to `main` completes lint, test, and build.
2. The workflow pushes `fastapi-backend:<git-sha>` and `:latest` to ECR.
3. The ECS task definition is rendered with the new image.
4. ECS performs a rolling deployment and waits for service stability.

Rollback: redeploy a previous image tag from ECR via the ECS console or re-run the workflow from an earlier commit on `main`.

## Troubleshooting

| Issue | Likely cause | Fix |
| --- | --- | --- |
| Tests fail on DB connection | PostgreSQL service not ready | Re-run workflow; health checks wait for `pg_isready`. |
| ECR login fails | Missing or invalid AWS credentials | Verify OIDC role or access keys and `AWS_REGION`. |
| Deploy skipped | Not a `main` push | Merge to `main` or use `workflow_dispatch` after configuring AWS. |
| Container unhealthy | Missing `DATABASE_URL` / migrations | Confirm Secrets Manager values and security groups. |
| Smoke test fails | App cannot start without DB | Smoke test uses SQLite; check Docker build logs for import errors. |

## Security notes

- Secrets are never committed; runtime values live in AWS Secrets Manager.
- The workflow uses minimal `permissions` (`contents: read`, `id-token: write`).
- Production deploys are gated to the `production` GitHub environment.
- Docker images run as a non-root `app` user.
