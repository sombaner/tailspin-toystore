# Tailspin Toys Deployment Guide

This guide provides detailed operational procedures for deploying the Tailspin Toys application to Azure Kubernetes Service (AKS) using automated GitHub Actions workflows.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Workflows](#deployment-workflows)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Verification](#verification)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Overview

The deployment automation consists of three GitHub Actions workflows:

1. **Infrastructure Deployment** (`infra-deploy.yml`) - Provisions AKS cluster and supporting Azure resources using Terraform
2. **Container Build and Scan** (`docker-build.yml`) - Builds Docker images, scans for vulnerabilities, and pushes to Azure Container Registry
3. **Application Deployment** (`app-deploy.yml`) - Deploys applications to AKS with automated rollback on failure

### Architecture Components

- **Azure AKS**: Kubernetes cluster (Automatic mode) with auto-scaling node pool
- **Azure Container Registry (ACR)**: Premium SKU for container images
- **Azure Virtual Network**: Networking infrastructure with AKS subnet
- **Azure Log Analytics**: Centralized logging and monitoring
- **Azure Application Insights**: Application performance monitoring
- **GitHub Actions**: CI/CD orchestration with OIDC authentication

### Deployment Flow

```
Infrastructure Deployment → Container Build & Scan → Application Deployment
        (Terraform)               (Docker + Trivy)        (Kubernetes)
```

## Prerequisites

Before deploying, ensure you have completed:

1. ✅ **Azure Setup**: Follow [azure-setup-guide.md](./azure-setup-guide.md) to configure:
   - Azure AD application for GitHub OIDC
   - Azure Storage account for Terraform state
   - GitHub repository secrets (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID)

2. ✅ **Terraform Backend**: Update `infra/backend.tf` with your storage account name

3. ✅ **Permissions**: Ensure the Azure service principal has Contributor role on the subscription or resource group

## Deployment Workflows

### 1. Infrastructure Deployment

**Workflow**: `.github/workflows/infra-deploy.yml`

**Purpose**: Provisions AKS cluster, ACR, networking, and monitoring resources using Terraform

**Triggers**:
- Manual dispatch (with plan/apply/destroy options)
- Push to `main` branch with changes in `infra/**`

**Jobs**:
- `terraform-plan`: Validates configuration and generates execution plan
- `terraform-apply`: Applies changes to Azure (requires approval)
- `terraform-destroy`: Destroys infrastructure (manual trigger only)

**Outputs**:
- AKS cluster name
- ACR login server URL
- Resource group name

### 2. Container Build and Scan

**Workflow**: `.github/workflows/docker-build.yml`

**Purpose**: Builds Docker images for server and client, scans for vulnerabilities, and pushes to ACR

**Triggers**:
- Manual dispatch
- Successful completion of Infrastructure Deployment workflow
- Push to `main` branch with changes in `server/**` or `client/**`

**Jobs**:
- `build-server`: Builds and scans Flask backend image
- `build-client`: Builds and scans Astro frontend image

**Security**: 
- Trivy vulnerability scanning blocks deployment on HIGH/CRITICAL CVEs
- Results uploaded to GitHub Security tab

**Outputs**:
- ACR login server URL
- Image tags (commit SHA, semantic version, latest)

### 3. Application Deployment

**Workflow**: `.github/workflows/app-deploy.yml`

**Purpose**: Deploys applications to AKS cluster with automated rollback

**Triggers**:
- Manual dispatch
- Successful completion of Container Build workflow
- Push to `main` branch with changes in `k8s/**`

**Jobs**:
- `deploy`: Applies Kubernetes manifests and verifies deployment

**Features**:
- Automatic namespace creation
- Dynamic image tag substitution
- LoadBalancer external IP provisioning
- Smoke tests for application health
- Automated rollback on failure
- Failure notification via GitHub Issues

**Outputs**:
- External IP address
- Deployment status

## Step-by-Step Deployment

### Initial Deployment (First Time)

#### Step 1: Deploy Infrastructure

1. Go to **Actions** → **Infrastructure Deployment**
2. Click **Run workflow**
3. Select **action**: `plan` (review changes first)
4. Click **Run workflow**
5. Review the Terraform plan in workflow logs
6. If plan looks correct, re-run workflow with **action**: `apply`
7. Wait for infrastructure provisioning (~10-15 minutes)

**Expected Results**:
- ✅ Resource group `rg-sb-aks-01` created in Central India
- ✅ AKS cluster running with 1-3 nodes
- ✅ ACR created and accessible
- ✅ Networking and monitoring configured

#### Step 2: Build and Scan Container Images

1. Go to **Actions** → **Container Build and Scan**
2. Click **Run workflow** → **Run workflow**
3. Wait for image builds and security scans (~5-10 minutes)

**Expected Results**:
- ✅ Server image built and pushed to ACR
- ✅ Client image built and pushed to ACR
- ✅ Trivy scans passed (no HIGH/CRITICAL vulnerabilities)
- ✅ Images tagged with commit SHA and semantic version

**If Scan Fails**:
- Review vulnerabilities in GitHub Security tab
- Update Dockerfiles to use patched base images
- Re-run workflow after fixes

#### Step 3: Deploy Applications to AKS

1. Go to **Actions** → **Application Deployment to AKS**
2. Click **Run workflow** → **Run workflow**
3. Wait for deployment and health checks (~5 minutes)

**Expected Results**:
- ✅ Namespace `tail-spin` created in AKS
- ✅ Server pods running and healthy
- ✅ Client pods running and healthy
- ✅ LoadBalancer external IP assigned
- ✅ Smoke tests passed

**If Deployment Fails**:
- Automatic rollback will restore previous version
- GitHub issue created with failure details
- Check troubleshooting section below

### Subsequent Deployments

For code changes after initial deployment:

1. **Code Changes**: Push changes to `main` branch or relevant paths
2. **Automatic Triggers**: Workflows automatically trigger based on changed paths:
   - `infra/**` changes → Infrastructure Deployment
   - `server/**` or `client/**` changes → Container Build → Application Deployment
   - `k8s/**` changes → Application Deployment

3. **Manual Trigger**: Use workflow dispatch for manual deployments

## Verification

### Verify Infrastructure

```bash
# Login to Azure
az login

# List AKS clusters
az aks list --resource-group rg-sb-aks-01 --output table

# Get AKS credentials
az aks get-credentials --resource-group rg-sb-aks-01 --name <aks-cluster-name>

# Check nodes
kubectl get nodes

# List ACR repositories
az acr repository list --name <acr-name> --output table
```

### Verify Deployments

```bash
# Check namespace
kubectl get namespace tail-spin

# Check deployments
kubectl get deployments -n tail-spin

# Check pods
kubectl get pods -n tail-spin

# Check pod logs
kubectl logs -n tail-spin -l app=tailspin-server --tail=50
kubectl logs -n tail-spin -l app=tailspin-client --tail=50

# Check services
kubectl get svc -n tail-spin

# Get external IP
kubectl get svc tailspin-client -n tail-spin -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Verify Application

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc tailspin-client -n tail-spin -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test client endpoint
curl -I http://$EXTERNAL_IP

# Open in browser
echo "Application URL: http://$EXTERNAL_IP"
```

## Monitoring

### Azure Monitor

1. Go to **Azure Portal** → **Resource Groups** → `rg-sb-aks-01`
2. Select **Log Analytics workspace** → **Logs**
3. Query container logs:
   ```kusto
   ContainerLog
   | where Namespace == "tail-spin"
   | order by TimeGenerated desc
   | take 100
   ```

### Application Insights

1. Go to **Azure Portal** → **Application Insights** → `appi-tailspin-prod`
2. View application map, performance metrics, and failures
3. Create custom queries and dashboards

### GitHub Actions Workflow Logs

1. Go to **Actions** tab in repository
2. Select workflow run
3. View job logs and step details
4. Download logs for offline analysis

### Kubernetes Events

```bash
# View events in namespace
kubectl get events -n tail-spin --sort-by='.lastTimestamp'

# Describe pod for detailed events
kubectl describe pod <pod-name> -n tail-spin

# Check resource usage
kubectl top pods -n tail-spin
kubectl top nodes
```

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues and solutions.

### Quick Checks

1. **Infrastructure deployment failed**
   - Check Terraform plan output for errors
   - Verify Azure quota for AKS and ACR
   - Ensure service principal has correct permissions

2. **Container build failed**
   - Review Trivy scan results for vulnerabilities
   - Check Dockerfile syntax and base images
   - Verify ACR access and authentication

3. **Application deployment failed**
   - Check pod logs: `kubectl logs -n tail-spin -l app=<app-name>`
   - Verify image pull: `kubectl describe pod <pod-name> -n tail-spin`
   - Check rollback status in workflow logs

4. **Application not accessible**
   - Verify LoadBalancer has external IP
   - Check service configuration: `kubectl get svc -n tail-spin`
   - Test connectivity: `curl http://<external-ip>`

## Rollback Procedures

See [rollback-procedures.md](./rollback-procedures.md) for detailed rollback steps.

### Quick Rollback

```bash
# Rollback Kubernetes deployments
kubectl rollout undo deployment/tailspin-server -n tail-spin
kubectl rollout undo deployment/tailspin-client -n tail-spin

# Verify rollback status
kubectl rollout status deployment/tailspin-server -n tail-spin
kubectl rollout status deployment/tailspin-client -n tail-spin
```

## Security Considerations

- ✅ GitHub OIDC authentication (no service principal secrets)
- ✅ Trivy vulnerability scanning blocks HIGH/CRITICAL CVEs
- ✅ Managed identity for AKS to ACR authentication
- ✅ Azure Key Vault for sensitive configuration (optional)
- ✅ Network policies for pod-to-pod communication (optional)
- ✅ RBAC for Kubernetes access control

## Cost Management

Monitor costs in Azure Cost Management:
- AKS cluster: Node pool VM costs (~$70-100/month for Standard_D2s_v3)
- ACR Premium: ~$10/month + storage costs
- Networking: LoadBalancer and egress traffic
- Monitoring: Log Analytics data ingestion

**Cost Optimization**:
- Scale down node count during off-hours
- Use Azure Reserved Instances for predictable workloads
- Implement auto-scaling based on demand
- Clean up unused images in ACR

## Next Steps

1. Configure custom domain and SSL certificate
2. Set up multi-environment deployments (dev, staging, prod)
3. Implement GitOps with ArgoCD or Flux
4. Add advanced monitoring and alerting
5. Configure backup and disaster recovery
6. Implement infrastructure drift detection

## References

- [Azure AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
