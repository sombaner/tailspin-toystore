# Implementation Plan: AKS Deployment Automation

**Branch**: `001-aks-deployment-automation` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-aks-deployment-automation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build end-to-end deployment automation using GitHub Actions to orchestrate Terraform-based AKS cluster provisioning in Azure Central India, followed by automated Docker image builds, security scanning, and Kubernetes application deployment. The system will provision an AKS automatic cluster in resource group "rg-sb-aks-01", push container images to Azure Container Registry, and deploy Tailspin server and client applications to the "tail-spin" namespace with external client access via LoadBalancer.

## Technical Context

**Language/Version**: 
- Infrastructure: Terraform 1.6+ with Azure provider 3.80+
- Application: Python 3.11 (server), Node.js 20 (client)
- CI/CD: GitHub Actions with YAML workflows

**Primary Dependencies**: 
- Terraform Azure provider (azurerm)
- Azure CLI 2.50+
- kubectl 1.28+
- Docker 24.0+
- Trivy (container scanning)
- GitHub OIDC provider for Azure authentication

**Storage**: 
- Terraform state: Azure Storage Account with blob container and state locking
- Container images: Azure Container Registry (Premium SKU)
- Application data: SQLite (existing, containerized with server)

**Testing**: 
- Infrastructure: terraform validate, terraform plan (dry-run)
- Containers: Trivy vulnerability scanning (block on HIGH/CRITICAL)
- Application: Post-deployment smoke tests via Playwright (tests/e2e/)
- Kubernetes: kubectl rollout status, health check probes

**Target Platform**: 
- Azure AKS (Kubernetes 1.28+) in Central India region
- GitHub Actions runners (ubuntu-latest)
- Public AKS cluster (API server publicly accessible)

**Project Type**: 
- Infrastructure as Code + CI/CD automation
- Existing web application deployment (Flask backend, Astro frontend)

**Performance Goals**: 
- Infrastructure provisioning: <15 minutes (AKS cluster ready)
- Container build + scan: <10 minutes per image
- Application deployment: <5 minutes (pods running)
- End-to-end pipeline: <30 minutes (code to production)

**Constraints**: 
- MUST use GitHub OIDC authentication (no service principal secrets)
- MUST use existing Kubernetes manifests (k8s/ directory)
- MUST implement rollback capability (<5 minutes recovery)
- MUST block deployment on container vulnerabilities (HIGH/CRITICAL)

**Scale/Scope**: 
- Single AKS cluster (auto-scaling enabled)
- 2 containerized applications (server, client)
- 3 GitHub Actions workflows (infra, docker, deploy)
- ~15 Terraform modules (AKS, ACR, networking, monitoring)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [Tailspin Toys Constitution](../../.specify/memory/constitution.md):

- [x] **I. IaC Excellence**: All Azure infrastructure (AKS, ACR, networking) defined in Terraform modules under `infra/` directory with remote state in Azure Storage backend and state locking enabled
- [x] **II. Pipeline Quality & Security**: GitHub Actions workflows (.github/workflows/infra-deploy.yml, docker-build.yml, app-deploy.yml) use GitHub OIDC authentication to Azure, explicit permissions blocks, and pre-deployment validation (terraform plan, Trivy scan)
- [x] **III. Test-First (NON-NEGOTIABLE)**: Post-deployment smoke tests written in Playwright (tests/e2e/); infrastructure tests via terraform validate/plan; container vulnerability scans before deployment
- [x] **IV. Container & K8s**: Docker images use existing Dockerfiles (server/Dockerfile, client/Dockerfile) with multi-stage builds; Kubernetes manifests (k8s/) specify resource requests/limits; AKS uses managed identity for ACR authentication
- [x] **V. Observability**: Pipeline structured logging via GitHub Actions; Application Insights integration for deployed apps; alerts configured for deployment failures and health check issues
- [x] **Security Standards**: GitHub OIDC for authentication (no secrets); Azure Key Vault for sensitive configuration; Trivy vulnerability scanning blocks HIGH/CRITICAL CVEs; least privilege RBAC for managed identities
- [x] **Deployment Management**: Initial deployment establishes foundation for multi-environment strategy; rollback via kubectl rollout undo and Terraform state management; smoke tests post-deployment mandatory

**Violations Requiring Justification**: 

1. **Single Environment (Initial)**: Starting with single AKS cluster deployment before establishing dev/staging/prod environments
   - **Rationale**: Foundation infrastructure must be proven working before replicating to multiple environments
   - **Alternatives Rejected**: Immediate multi-environment deployment would multiply complexity and risk during initial automation development
   - **Remediation**: Phase 2 will extend Terraform with environment variables and GitHub Environments for dev/staging/prod separation (Target: Sprint 2)

2. **Public AKS Cluster**: Deploying public cluster (API server publicly accessible) per explicit requirement
   - **Rationale**: User requirement specifies "public as well as an AKS automatic cluster"
   - **Alternatives Rejected**: Private cluster would require VPN/Azure Bastion for access, adding infrastructure complexity not in scope
   - **Remediation**: Production deployment should evaluate private cluster with Azure Private Link (Future: Production hardening phase)

## Project Structure

### Documentation (this feature)

```text
specs/001-aks-deployment-automation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (infrastructure resources)
├── quickstart.md        # Phase 1 output (deployment runbook)
├── contracts/           # Phase 1 output (Terraform module interfaces)
│   ├── aks-module.md
│   ├── acr-module.md
│   ├── networking-module.md
│   └── monitoring-module.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Infrastructure as Code
infra/
├── main.tf                       # Root module orchestration
├── variables.tf                  # Environment variables
├── outputs.tf                    # Output values (cluster endpoint, ACR URL)
├── backend.tf                    # Azure Storage backend configuration
├── providers.tf                  # Azure provider with OIDC auth
├── terraform.tfvars              # Variable values (Central India, rg-sb-aks-01)
└── modules/
    ├── aks/                      # AKS cluster module
    │   ├── main.tf               # AKS automatic cluster resource
    │   ├── variables.tf          # Cluster configuration inputs
    │   └── outputs.tf            # Cluster ID, endpoint, kubeconfig
    ├── acr/                      # Azure Container Registry module
    │   ├── main.tf               # ACR Premium resource
    │   ├── variables.tf          # Registry configuration
    │   └── outputs.tf            # ACR login server, ID
    ├── networking/               # Virtual Network module
    │   ├── main.tf               # VNet, subnets for AKS
    │   ├── variables.tf          # Network CIDR blocks
    │   └── outputs.tf            # Subnet IDs
    ├── monitoring/               # Azure Monitor module
    │   ├── main.tf               # Log Analytics, Application Insights
    │   ├── variables.tf          # Retention, alert configs
    │   └── outputs.tf            # Workspace IDs, instrumentation keys
    └── rbac/                     # Role assignments module
        ├── main.tf               # AKS to ACR managed identity RBAC
        ├── variables.tf          # Principal IDs, scope
        └── outputs.tf            # Role assignment IDs

# CI/CD Workflows
.github/
└── workflows/
    ├── infra-deploy.yml          # Terraform infrastructure provisioning
    ├── docker-build.yml          # Container image build & scan
    └── app-deploy.yml            # Kubernetes application deployment

# Kubernetes Manifests (existing, will be updated)
k8s/
├── namespace.yaml                # tail-spin namespace
├── server-deployment.yaml        # Flask backend (add resource limits, probes)
├── client-deployment.yaml        # Astro frontend (add resource limits, probes)
└── client-service.yaml           # LoadBalancer service (NEW - external access)

# Application Code (existing, no changes for this feature)
server/
├── Dockerfile                    # Multi-stage Flask image
└── [existing Flask application]

client/
├── Dockerfile                    # Multi-stage Astro image
└── [existing Astro application]

# Testing (existing + new smoke tests)
tests/
└── e2e/
    ├── deployment-smoke.spec.ts  # NEW - Post-deployment health checks
    └── [existing E2E tests]
```

**Structure Decision**: Infrastructure as Code project structure with Terraform modules for Azure resources (AKS, ACR, networking, monitoring). GitHub Actions workflows orchestrate the three-phase deployment: infrastructure provisioning → container builds → application deployment. Existing Kubernetes manifests will be enhanced with resource limits and LoadBalancer service. No application code changes required.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Single Environment (Initial) | Foundation infrastructure must be proven working before multi-environment replication | Immediate multi-environment deployment multiplies complexity during initial automation development; increases failure modes and debugging surface area |
| Public AKS Cluster | Explicit user requirement and reduces initial infrastructure complexity | Private cluster requires VPN/Azure Bastion/jumpbox infrastructure not in current scope; adds networking complexity that delays core deployment automation |

---

## Phase Completion Status

### Phase 0: Outline & Research ✅ COMPLETE

**Deliverable**: [research.md](./research.md)

**Completed**:
- ✅ Resolved all NEEDS CLARIFICATION items from Technical Context
- ✅ Researched AKS Automatic cluster configuration best practices
- ✅ Determined GitHub OIDC to Azure authentication pattern
- ✅ Defined Terraform state management with Azure Storage backend
- ✅ Selected Trivy for container vulnerability scanning
- ✅ Established Kubernetes resource limits based on Flask/Node.js profiles
- ✅ Documented Azure Managed Identity for ACR authentication
- ✅ Designed GitHub Actions workflow orchestration strategy
- ✅ Defined rollback strategies for Kubernetes and Terraform

**Key Decisions**:
- Infrastructure: Terraform with Azure Storage backend, AKS automatic mode, GitHub OIDC authentication
- Security: Trivy vulnerability scanning, managed identities, no secrets in code
- Deployment: Three-phase GitHub Actions workflows with automated rollback
- Resource Management: Conservative Kubernetes limits, health probes for all deployments

---

### Phase 1: Design & Contracts ✅ COMPLETE

**Deliverables**:
- ✅ [data-model.md](./data-model.md) - Infrastructure entities and relationships
- ✅ [contracts/aks-module.md](./contracts/aks-module.md) - AKS cluster Terraform module interface
- ✅ [contracts/acr-module.md](./contracts/acr-module.md) - Azure Container Registry module interface
- ✅ [contracts/networking-module.md](./contracts/networking-module.md) - Virtual Network module interface
- ✅ [contracts/monitoring-module.md](./contracts/monitoring-module.md) - Log Analytics & App Insights module interface
- ✅ [quickstart.md](./quickstart.md) - Deployment runbook with step-by-step procedures

**Completed**:
- ✅ Defined 11 infrastructure and Kubernetes entities (Resource Group, AKS, ACR, VNet, Log Analytics, App Insights, RBAC, Namespace, Deployments, Services)
- ✅ Established entity relationships and lifecycle management
- ✅ Created Terraform module contracts for all infrastructure components
- ✅ Documented module inputs, outputs, validation rules, and usage examples
- ✅ Generated comprehensive deployment runbook with prerequisites, workflows, troubleshooting, and rollback procedures
- ✅ Updated agent context file (.github/agents/copilot-instructions.md)

**Design Validation**:
- ✅ All Terraform modules follow Constitution Principle I (IaC Excellence)
- ✅ Module interfaces support GitHub OIDC authentication (Principle II)
- ✅ Resource limits specified for all Kubernetes deployments (Principle IV)
- ✅ Monitoring and observability integrated via Log Analytics and Application Insights (Principle V)
- ✅ Security best practices enforced (managed identities, no hardcoded credentials, vulnerability scanning)

---

### Phase 2: Tasks Breakdown (NOT STARTED)

**Deliverable**: tasks.md (created by `/speckit.tasks` command)

**Next Steps**:
1. Run `/speckit.tasks` command to generate implementation task breakdown
2. Task list will include:
   - Terraform module implementation (infra/modules/)
   - GitHub Actions workflow creation (.github/workflows/)
   - Kubernetes manifest updates (k8s/)
   - Post-deployment smoke tests (tests/e2e/)
   - Documentation updates

**Notes**:
- Phase 2 planning is intentionally deferred until Phase 0 and Phase 1 artifacts are reviewed
- Task generation will reference data-model.md entities and module contracts for implementation details

---

## Re-Evaluated Constitution Check (Post-Design)

*Required after Phase 1 completion per Constitution Check gate*

Verify compliance with [Tailspin Toys Constitution](../../.specify/memory/constitution.md):

- [x] **I. IaC Excellence**: ✅ All Azure infrastructure defined in Terraform modules under `infra/` with remote state in Azure Storage backend and state locking enabled. Modules follow HashiCorp style guide with clear inputs/outputs/validation.
- [x] **II. Pipeline Quality & Security**: ✅ GitHub Actions workflows designed with GitHub OIDC authentication, explicit permissions blocks, and pre-deployment validation (terraform plan, Trivy scan). Workflow contracts defined in research.md.
- [x] **III. Test-First (NON-NEGOTIABLE)**: ✅ Post-deployment smoke tests defined in quickstart.md; infrastructure tests via terraform validate/plan; container vulnerability scans before deployment. Test execution integrated into app-deploy workflow.
- [x] **IV. Container & K8s**: ✅ Docker images use existing Dockerfiles with multi-stage builds. Kubernetes manifests (data-model.md) specify resource requests/limits and health probes. AKS uses managed identity for ACR authentication (no image pull secrets).
- [x] **V. Observability**: ✅ Pipeline structured logging via GitHub Actions. Application Insights integration defined in monitoring module. Alerts configured for deployment failures and health check issues in quickstart.md.
- [x] **Security Standards**: ✅ GitHub OIDC for authentication (no secrets in workflows). Azure Key Vault integration path documented. Trivy vulnerability scanning blocks HIGH/CRITICAL CVEs. Least privilege RBAC for managed identities enforced via rbac module.
- [x] **Deployment Management**: ✅ Rollback strategy defined in quickstart.md (kubectl rollout undo for apps, Terraform state restoration for infrastructure). Smoke tests mandatory post-deployment. Multi-environment expansion path documented in Complexity Tracking.

**Post-Design Compliance**: ✅ **PASS**

All constitutional principles satisfied in design phase. No new violations introduced. Documented violations (single environment, public cluster) remain justified with remediation plans.

---

## Summary

**Status**: Ready for implementation (Phase 2 task generation)

**Branch**: `001-aks-deployment-automation`

**Artifacts Generated**:
- Implementation plan (this file)
- Research document with technical decisions
- Data model with infrastructure entities
- Terraform module contracts (4 modules)
- Deployment runbook with operational procedures
- Agent context file updated

**Next Command**: `/speckit.tasks` to generate implementation task breakdown

**Estimated Implementation Time**: 
- Terraform modules: 8-12 hours
- GitHub Actions workflows: 4-6 hours
- Kubernetes manifest updates: 2-3 hours
- Testing and validation: 3-4 hours
- **Total**: 17-25 hours (2-3 sprints)
