# Kubernetes deployment

This directory contains Kustomize manifests for running the NestJS API on any
cloud-managed Kubernetes cluster (EKS, GKE, AKS, or others with the NGINX Ingress
Controller).

## Layout

| Path | Purpose |
| ---- | ------- |
| `base/` | Shared Deployment, Service, Ingress, HPA, migration Job |
| `overlays/development` | Single-replica development namespace |
| `overlays/staging` | Pre-production sizing and hostnames |
| `overlays/production` | HA sizing, TLS, and PodDisruptionBudget |
| `secrets/backend-api-secrets.example.env` | Template for required Secret keys |

## Service discovery

In-cluster clients reach the API through the ClusterIP Service DNS name:

`backend-api.<namespace>.svc.cluster.local`

For example, in production:

`backend-api.backend-api-production.svc.cluster.local`

## Load balancing

External traffic enters through the Ingress resource, which fronts the Service
and distributes requests across ready pods (via the ingress controller’s
round-robin upstream). The HorizontalPodAutoscaler scales pod replicas based on
CPU and memory utilization.

## Prerequisites

1. Container image published (for example `ghcr.io/<owner>/<repo>:production-latest`)
2. NGINX Ingress Controller installed in the cluster
3. TLS certificate material (or cert-manager) for staging and production hosts
4. Kubernetes Secret `backend-api-secrets` in the target namespace

```bash
kubectl create secret generic backend-api-secrets \
  --namespace backend-api-production \
  --from-env-file=deploy/kubernetes/secrets/backend-api-secrets.env
```

Update `newName` in each overlay `kustomization.yaml` to your registry path
before the first deploy.

## Apply an overlay

```bash
# Validate rendered manifests
bash scripts/kube-validate.sh

# Deploy
bash scripts/kube-deploy.sh production

# Apply database migrations inside the cluster (optional when CI already migrated)
kubectl -n backend-api-production apply -k deploy/kubernetes/overlays/production \
  --dry-run=client -o yaml | kubectl apply -f -  # ensures namespace exists first
kubectl -n backend-api-production delete job backend-api-migrate --ignore-not-found
kubectl -n backend-api-production apply -f deploy/kubernetes/base/migration-job.yaml
kubectl -n backend-api-production wait --for=condition=complete job/backend-api-migrate --timeout=300s
```

GitHub Actions can roll out new images with `scripts/deploy.sh` when
`KUBE_NAMESPACE` and `KUBE_DEPLOYMENT=backend-api` are configured.