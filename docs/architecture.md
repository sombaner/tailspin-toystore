# Architecture Overview

This document describes the architecture of the Tailspin Toys AKS deployment automation system.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GitHub Repository                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Terraform   │  │   Docker     │  │  Kubernetes  │                  │
│  │  (infra/)    │  │  (server/    │  │  (k8s/)      │                  │
│  │              │  │   client/)   │  │              │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ GitHub Actions (OIDC)
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Azure Cloud Platform                               │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    Resource Group: rg-sb-aks-01                 │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐     │   │
│  │  │           Azure Kubernetes Service (AKS)             │     │   │
│  │  │                                                       │     │   │
│  │  │  Namespace: tail-spin                                │     │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐         │     │   │
│  │  │  │ tailspin-server  │  │ tailspin-client  │         │     │   │
│  │  │  │  (Flask API)     │  │  (Astro UI)      │         │     │   │
│  │  │  │                  │  │                  │         │     │   │
│  │  │  │ Pods: 1          │  │ Pods: 1          │         │     │   │
│  │  │  │ CPU: 250m-1000m  │  │ CPU: 100m-500m   │         │     │   │
│  │  │  │ Mem: 512Mi-1Gi   │  │ Mem: 256Mi-512Mi │         │     │   │
│  │  │  └──────────────────┘  └──────────────────┘         │     │   │
│  │  │           │                      │                   │     │   │
│  │  │  ┌────────▼────────┐  ┌─────────▼─────────┐         │     │   │
│  │  │  │ ClusterIP       │  │ LoadBalancer      │         │     │   │
│  │  │  │ Service         │  │ Service           │         │     │   │
│  │  │  │ Port: 5100      │  │ Port: 80          │         │     │   │
│  │  │  └─────────────────┘  └─────────┬─────────┘         │     │   │
│  │  │                                  │                   │     │   │
│  │  └──────────────────────────────────┼───────────────────┘     │   │
│  │                                     │ External IP             │   │
│  │                                     ▼                          │   │
│  │                              Internet Users                    │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────┐     │   │
│  │  │      Azure Container Registry (Premium)              │     │   │
│  │  │                                                       │     │   │
│  │  │  Repositories:                                        │     │   │
│  │  │  - tailspin-server:latest, v1.0.0, <commit-sha>     │     │   │
│  │  │  - tailspin-client:latest, v1.0.0, <commit-sha>     │     │   │
│  │  │                                                       │     │   │
│  │  │  Features:                                            │     │   │
│  │  │  - Geo-replication ready                             │     │   │
│  │  │  - Vulnerability scanning                            │     │   │
│  │  └──────────────────────────────────────────────────────┘     │   │
│  │                          ▲                                     │   │
│  │                          │ Managed Identity (AcrPull)          │   │
│  │                          │                                     │   │
│  │  ┌──────────────────────────────────────────────────────┐     │   │
│  │  │           Azure Virtual Network                       │     │   │
│  │  │                                                       │     │   │
│  │  │  Address Space: 10.0.0.0/16                          │     │   │
│  │  │  ┌────────────────────────────────────────┐          │     │   │
│  │  │  │  AKS Subnet: 10.0.1.0/24               │          │     │   │
│  │  │  │  - System node pool (1-3 nodes)        │          │     │   │
│  │  │  │  - Auto-scaling enabled                │          │     │   │
│  │  │  └────────────────────────────────────────┘          │     │   │
│  │  └──────────────────────────────────────────────────────┘     │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────┐     │   │
│  │  │           Azure Monitor & Logging                     │     │   │
│  │  │                                                       │     │   │
│  │  │  ┌────────────────────────────────────────┐          │     │   │
│  │  │  │  Log Analytics Workspace               │          │     │   │
│  │  │  │  - Container logs                      │          │     │   │
│  │  │  │  - Kubernetes events                   │          │     │   │
│  │  │  │  - Retention: 30 days                  │          │     │   │
│  │  │  └────────────────────────────────────────┘          │     │   │
│  │  │                                                       │     │   │
│  │  │  ┌────────────────────────────────────────┐          │     │   │
│  │  │  │  Application Insights                  │          │     │   │
│  │  │  │  - Request telemetry                   │          │     │   │
│  │  │  │  - Dependency tracking                 │          │     │   │
│  │  │  │  - Performance metrics                 │          │     │   │
│  │  │  └────────────────────────────────────────┘          │     │   │
│  │  └──────────────────────────────────────────────────────┘     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │           Resource Group: rg-terraform-state                    │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐      │   │
│  │  │        Azure Storage Account                          │      │   │
│  │  │                                                       │      │   │
│  │  │  Container: tfstate                                   │      │   │
│  │  │  - tailspin-aks.tfstate                              │      │   │
│  │  │  - State locking via blob lease                      │      │   │
│  │  │  - Versioning enabled                                │      │   │
│  │  └──────────────────────────────────────────────────────┘      │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflows                          │
└─────────────────────────────────────────────────────────────────────────┘

1. Infrastructure Deployment (infra-deploy.yml)
   ┌──────────────────────────────────────────────────────────┐
   │  Trigger: Push to infra/** or workflow_dispatch          │
   │                                                           │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │   Azure     │  │  Terraform  │  │  Terraform  │     │
   │  │   Login     │─▶│    Init     │─▶│   Validate  │     │
   │  │   (OIDC)    │  │             │  │             │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │         │                                                │
   │         ▼                                                │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │  Terraform  │  │  Terraform  │  │   Verify    │     │
   │  │    Plan     │─▶│    Apply    │─▶│   Cluster   │     │
   │  │             │  │  (approval) │  │             │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │                                                          │
   │  Outputs: AKS cluster name, ACR login server            │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
2. Container Build & Scan (docker-build.yml)
   ┌──────────────────────────────────────────────────────────┐
   │  Trigger: Infra deploy success, Push to server/client/** │
   │                                                           │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │   Azure     │  │   Get ACR   │  │    Build    │     │
   │  │   Login     │─▶│   Details   │─▶│   Docker    │     │
   │  │   (OIDC)    │  │             │  │   Images    │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │         │                                                │
   │         ▼                                                │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │    Trivy    │  │   Upload    │  │    Push     │     │
   │  │   Scan      │─▶│  Security   │─▶│  to ACR     │     │
   │  │(BLOCK HIGH) │  │   Results   │  │             │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │                                                          │
   │  Parallel Jobs: build-server, build-client              │
   │  Outputs: ACR login server, Image tags                  │
   └──────────────────────────────────────────────────────────┘
                            │
                            ▼
3. Application Deployment (app-deploy.yml)
   ┌──────────────────────────────────────────────────────────┐
   │  Trigger: Container build success, Push to k8s/**        │
   │                                                           │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │   Azure     │  │  Configure  │  │   Create    │     │
   │  │   Login     │─▶│   kubectl   │─▶│  Namespace  │     │
   │  │   (OIDC)    │  │             │  │             │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │         │                                                │
   │         ▼                                                │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │   Update    │  │    Apply    │  │    Wait     │     │
   │  │  Manifests  │─▶│  K8s YAML   │─▶│  Rollout    │     │
   │  │ (Image URL) │  │             │  │   Status    │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │         │                                                │
   │         ▼                                                │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
   │  │ Get Ext IP  │  │   Smoke     │  │  Rollback   │     │
   │  │(LoadBalancer│─▶│   Tests     │─▶│ (on failure)│     │
   │  │             │  │             │  │             │     │
   │  └─────────────┘  └─────────────┘  └─────────────┘     │
   │                                                          │
   │  Outputs: External IP, Deployment status                │
   └──────────────────────────────────────────────────────────┘
```

## Technology Stack

### Infrastructure as Code
- **Terraform**: v1.6.0+
  - Azure provider (azurerm) v3.80+
  - Remote state: Azure Storage backend with locking
  - Modules: networking, monitoring, ACR, AKS, RBAC

### Azure Resources
- **AKS (Azure Kubernetes Service)**: v1.28+
  - Mode: Automatic (auto-scaling, auto-updates)
  - Node pool: Standard_D2s_v3, 1-3 nodes
  - Network plugin: Azure CNI
  - Authentication: System-assigned managed identity

- **ACR (Azure Container Registry)**: Premium SKU
  - Geo-replication capable
  - Vulnerability scanning integrated
  - Authentication: Managed identity from AKS

- **Networking**:
  - Virtual Network: 10.0.0.0/16
  - AKS Subnet: 10.0.1.0/24
  - LoadBalancer: Azure Standard SKU
  - Service CIDR: 10.1.0.0/16

- **Monitoring**:
  - Log Analytics Workspace: 30-day retention
  - Application Insights: Web application type
  - Container Insights: Enabled on AKS

### Application Stack
- **Backend**: Python 3.11 with Flask
  - SQLAlchemy ORM
  - SQLite database (ephemeral, in container)
  - API endpoints: /api/games, /api/games/{id}

- **Frontend**: Node.js 20 with Astro
  - Svelte components for interactivity
  - Static site generation
  - API integration with backend

### CI/CD
- **GitHub Actions**: Ubuntu-latest runners
  - Authentication: OIDC (no secrets)
  - Workflows: Infrastructure, Container Build, App Deploy
  - Security scanning: Trivy for container vulnerabilities

### Containerization
- **Docker**: Multi-stage builds
  - Server base: python:3.11-slim
  - Client base: node:lts (later stages use alpine)
  - Image tagging: commit SHA, semantic version, latest

## Security Architecture

### Authentication & Authorization
```
GitHub Actions                Azure Resources
      │                             │
      │ OIDC Token Exchange          │
      ├─────────────────────────────▶│
      │                              │
      │ Federated Credential         │
      │ (no secrets!)                │
      │                              │
      └─────────────────────────────▶│
                                     │
                                     ▼
                          Azure AD Application
                                     │
                                     │ Contributor Role
                                     ▼
                          Azure Subscription
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                          ▼                     ▼
                    Resource Groups       ACR, AKS, etc.
```

### Container Security
```
Code Push → Build → Trivy Scan → Block if HIGH/CRITICAL → Push to ACR
                         │
                         ▼
                   GitHub Security Tab
                   (SARIF upload)
```

### Network Security
- AKS API server: Public endpoint (configurable to private)
- Pod-to-pod: Azure Network Policy
- External access: LoadBalancer with Azure Standard SKU
- ACR access: Managed identity (no image pull secrets)

## Monitoring & Observability

### Metrics Flow
```
Application Pods
       │
       ├─── Container Logs ─────────────▶ Log Analytics Workspace
       │                                         │
       ├─── Performance Metrics ────────▶ Application Insights
       │                                         │
       └─── Kubernetes Events ──────────▶ Container Insights
                                                 │
                                                 ▼
                                         Azure Monitor Dashboards
                                                 │
                                                 ▼
                                         Alert Rules (future)
                                           - Error rate > 1%
                                           - Response P95 > 2s
                                           - Pod crash loops
```

### Logging Standards
- Format: JSON structured logs (where applicable)
- Fields: timestamp, level, message, correlation_id, service, environment
- Retention: 30 days (Log Analytics)

## Deployment Patterns

### Blue-Green Deployment (Current)
- Old version remains available during new deployment
- Automatic rollback on failure
- Zero-downtime deployments

### Rollback Strategy
```
Failure Detected
       │
       ├─── Health Check Failure ────▶ kubectl rollout undo
       │
       ├─── Smoke Test Failure ──────▶ kubectl rollout undo
       │
       └─── Timeout ─────────────────▶ kubectl rollout undo
                                              │
                                              ▼
                                      Previous Version Restored
                                              │
                                              ▼
                                       GitHub Issue Created
```

## Scaling Considerations

### Current Capacity
- AKS Nodes: 1-3 (auto-scaling enabled)
- Server Pods: 1 replica
- Client Pods: 1 replica

### Future Scaling Options
1. **Horizontal Pod Autoscaling (HPA)**
   - Scale pods based on CPU/memory
   - Target: 70% CPU utilization

2. **Cluster Autoscaling**
   - Already enabled (node pool: 1-3)
   - Can increase max nodes as needed

3. **Multi-Region Deployment**
   - ACR geo-replication ready (Premium SKU)
   - Traffic Manager for multi-region routing
   - Separate AKS clusters per region

## Disaster Recovery

### Backup Strategy
- **Infrastructure**: Terraform state versioning in Azure Storage
- **Application Code**: Git repository (source of truth)
- **Container Images**: ACR with geo-replication
- **Configuration**: Kubernetes manifests in Git
- **Data**: SQLite ephemeral (stateless application)

### Recovery Procedures
- Infrastructure: `terraform apply` from last known good state
- Application: Re-deploy from previous commit
- Complete rebuild: Run all workflows from scratch (~30 minutes)

## Cost Optimization

### Current Monthly Costs (Estimate)
- AKS cluster: ~$70-100 (Standard_D2s_v3 nodes)
- ACR Premium: ~$10 + storage
- Load Balancer: ~$20
- Networking: Variable (egress traffic)
- Monitoring: ~$5-10 (Log Analytics ingestion)
- **Total**: ~$100-150/month

### Optimization Strategies
- Scale down during off-hours
- Use Azure Reserved Instances
- Implement resource right-sizing
- Clean up unused ACR images

## Future Enhancements

1. **Multi-Environment Support**
   - Dev, Staging, Production environments
   - Terraform workspaces or separate tfvars
   - GitHub Environments with approvals

2. **Advanced Networking**
   - Private AKS cluster
   - Azure Application Gateway with WAF
   - Network policies for pod isolation

3. **Enhanced Monitoring**
   - Azure Monitor dashboards
   - Alert rules and action groups
   - PagerDuty integration

4. **GitOps**
   - ArgoCD or Flux for declarative deployments
   - Git as single source of truth
   - Automated drift detection

5. **Stateful Workloads**
   - PersistentVolumeClaims for database
   - Azure Database for PostgreSQL
   - Backup and restore procedures

## References

- [Terraform Module Documentation](../specs/001-aks-deployment-automation/contracts/)
- [Deployment Guide](./deployment-guide.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Rollback Procedures](./rollback-procedures.md)
- [Azure Setup Guide](./azure-setup-guide.md)
