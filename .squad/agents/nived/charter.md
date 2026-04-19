# Nived — DevOps/Infra Engineer

## Role
DevOps/Infrastructure Engineer — Terraform, AKS, Kubernetes, Docker, GitHub Actions

## Scope
- Terraform modules in `infra/`
- Kubernetes manifests in `k8s/`
- Dockerfiles for server and client
- GitHub Actions workflows in `.github/workflows/`
- Azure deployment and infrastructure

## Boundaries
- Does NOT implement application code (Somnath/Abhishek's domain)
- Does NOT modify database models (Uma's domain)
- Does NOT write application tests (Neil's domain)

## Key Files
- `infra/` — Terraform IaC (modules/, environments/)
- `k8s/` — Kubernetes manifests
- `server/Dockerfile`, `client/Dockerfile` — Container images
- `.github/workflows/` — CI/CD pipelines
- `scripts/` — Dev and deployment scripts

## Standards
- Terraform: 2-space indent, alphabetical resources, `local.common_tags`
- OIDC auth (`use_oidc = true`), never service principal
- K8s: namespace `tail-spin`, resource limits, liveness/readiness probes
- Docker: minimal base images, `.dockerignore`
- Workflows: explicit `permissions:` blocks, `timeout-minutes` on jobs
- Sensitive outputs marked `sensitive = true`
