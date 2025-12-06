# Research: AKS Deployment Automation

**Date**: 2025-12-07  
**Feature**: 001-aks-deployment-automation  
**Phase**: 0 - Outline & Research

## Research Questions

Based on Technical Context analysis, the following areas required research:

1. **AKS Automatic Cluster Configuration**: Best practices for AKS automatic mode
2. **GitHub OIDC to Azure Authentication**: Setup and configuration patterns
3. **Terraform State Management**: Azure Storage backend configuration
4. **Container Vulnerability Scanning**: Trivy integration in GitHub Actions
5. **Kubernetes Resource Limits**: Appropriate values for Flask and Astro applications
6. **Azure Managed Identity for ACR**: AKS to ACR authentication patterns
7. **GitHub Actions Workflow Orchestration**: Multi-workflow dependencies and triggers
8. **Rollback Strategies**: Kubernetes and Terraform rollback mechanisms

---

## Research Findings

### 1. AKS Automatic Cluster Configuration

**Decision**: Use AKS automatic mode with system node pool auto-scaling

**Rationale**: 
- AKS automatic mode (introduced in 2024) provides managed node scaling, upgrades, and optimization
- Reduces operational overhead for cluster management
- Aligns with Constitution Principle IV (managed services where possible)
- Central India region fully supports AKS automatic clusters

**Implementation Details**:
```hcl
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-tailspin-prod"
  location            = "centralindia"
  resource_group_name = "rg-sb-aks-01"
  dns_prefix          = "tailspin"
  
  # AKS Automatic mode
  sku_tier            = "Standard"
  automatic_upgrade_channel = "stable"
  
  default_node_pool {
    name                = "systempool"
    vm_size             = "Standard_DS2_v2"
    auto_scaling_enabled = true
    min_count           = 1
    max_count           = 3
    vnet_subnet_id      = azurerm_subnet.aks.id
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  # Public cluster (per requirement)
  api_server_access_profile {
    authorized_ip_ranges = [] # Public access
  }
}
```

**Alternatives Considered**:
- Standard AKS cluster with manual node pool management: Rejected due to increased operational complexity
- Private AKS cluster: Rejected per explicit "public cluster" requirement

**References**:
- AKS automatic documentation (Azure docs)
- Terraform azurerm_kubernetes_cluster resource schema

---

### 2. GitHub OIDC to Azure Authentication

**Decision**: Use GitHub OIDC with federated identity credentials for Azure authentication

**Rationale**:
- Eliminates service principal secrets in GitHub Secrets (Constitution Principle II)
- Provides short-lived tokens with automatic rotation
- Reduces credential management overhead and security risks
- Supported by azure/login@v1 GitHub Action

**Implementation Details**:

**Azure Setup** (one-time, manual or separate Terraform):
```bash
# Create Azure AD Application
az ad app create --display-name "github-actions-tailspin"

# Create federated credential for GitHub repository
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "github-tailspin-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:github-samples/agents-in-sdlc:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Assign Contributor role to subscription
az role assignment create \
  --assignee <APP_ID> \
  --role Contributor \
  --scope /subscriptions/<SUBSCRIPTION_ID>
```

**GitHub Secrets** (configure in repository settings):
- `AZURE_CLIENT_ID`: Application (client) ID
- `AZURE_TENANT_ID`: Directory (tenant) ID  
- `AZURE_SUBSCRIPTION_ID`: Subscription ID

**GitHub Actions Workflow**:
```yaml
name: Infrastructure Deploy

on:
  workflow_dispatch:
  push:
    branches: [main]
    paths: ['infra/**']

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Terraform Apply
        run: terraform apply -auto-approve
```

**Alternatives Considered**:
- Service Principal with secret: Rejected due to Constitution requirement and security risks
- Managed Identity: Not available for GitHub-hosted runners

**References**:
- GitHub OIDC documentation
- Azure federated identity credentials guide

---

### 3. Terraform State Management

**Decision**: Store Terraform state in Azure Storage with blob lease locking

**Rationale**:
- Remote state enables team collaboration and CI/CD automation
- State locking prevents concurrent modifications causing corruption
- Azure Storage provides built-in redundancy and security
- Native integration with Terraform azurerm backend

**Implementation Details**:

**Azure Storage Setup** (one-time):
```bash
# Create storage account for Terraform state
az storage account create \
  --name sttailspintfstate \
  --resource-group rg-sb-aks-01 \
  --location centralindia \
  --sku Standard_LRS \
  --encryption-services blob

# Create container for state files
az storage container create \
  --name tfstate \
  --account-name sttailspintfstate
```

**Terraform Backend Configuration** (`infra/backend.tf`):
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-sb-aks-01"
    storage_account_name = "sttailspintfstate"
    container_name       = "tfstate"
    key                  = "tailspin-aks.tfstate"
    use_oidc             = true  # Use GitHub OIDC credentials
  }
}
```

**State Locking**:
- Automatic via Azure Storage blob lease mechanism
- No additional configuration required
- Lock timeout: 15 minutes (default)

**Alternatives Considered**:
- Terraform Cloud: Rejected to minimize external dependencies and costs
- Local state: Rejected due to team collaboration requirements

**References**:
- Terraform azurerm backend documentation
- Azure Storage state locking behavior

---

### 4. Container Vulnerability Scanning

**Decision**: Use Trivy for container vulnerability scanning in GitHub Actions

**Rationale**:
- Open-source, comprehensive vulnerability database (CVE, OS packages, app dependencies)
- Native GitHub Actions integration via aquasecurity/trivy-action
- Supports blocking pipeline on HIGH/CRITICAL vulnerabilities
- Faster than alternatives (Snyk requires authentication setup)

**Implementation Details**:

**GitHub Actions Workflow** (`.github/workflows/docker-build.yml`):
```yaml
name: Docker Build & Scan

on:
  push:
    branches: [main]
    paths: ['server/**', 'client/**']

permissions:
  contents: read
  security-events: write  # For SARIF upload

jobs:
  build-server:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Server Image
        run: |
          docker build -t tailspin-server:${{ github.sha }} ./server
      
      - name: Scan Server Image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: tailspin-server:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Fail pipeline on vulnerabilities
      
      - name: Upload Scan Results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Push to ACR
        run: |
          az acr login --name <ACR_NAME>
          docker tag tailspin-server:${{ github.sha }} <ACR_NAME>.azurecr.io/tailspin-server:${{ github.sha }}
          docker push <ACR_NAME>.azurecr.io/tailspin-server:${{ github.sha }}
```

**Vulnerability Thresholds**:
- **CRITICAL**: Block deployment immediately
- **HIGH**: Block deployment immediately  
- **MEDIUM/LOW**: Log and continue (monitor trends)

**Alternatives Considered**:
- Snyk: Rejected due to additional authentication complexity for free tier
- Azure Defender for Containers: Requires ACR Premium and introduces delay
- Docker Scout: Less comprehensive vulnerability database

**References**:
- Trivy documentation
- aquasecurity/trivy-action GitHub Action

---

### 5. Kubernetes Resource Limits

**Decision**: Set conservative resource requests/limits based on container profiles

**Rationale**:
- Constitution Principle IV requires resource limits for all Kubernetes resources
- Prevents resource exhaustion and pod eviction
- Enables horizontal pod autoscaling based on utilization
- Values based on Flask/Node.js application profiles

**Implementation Details**:

**Server (Flask Backend)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tailspin-server
  namespace: tail-spin
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: server
        image: <ACR>.azurecr.io/tailspin-server:latest
        resources:
          requests:
            cpu: "250m"      # 0.25 CPU cores
            memory: "512Mi"  # 512 MiB RAM
          limits:
            cpu: "1000m"     # 1 CPU core max
            memory: "1Gi"    # 1 GiB RAM max
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Client (Astro Frontend)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tailspin-client
  namespace: tail-spin
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: client
        image: <ACR>.azurecr.io/tailspin-client:latest
        resources:
          requests:
            cpu: "100m"      # 0.1 CPU cores
            memory: "256Mi"  # 256 MiB RAM
          limits:
            cpu: "500m"      # 0.5 CPU core max
            memory: "512Mi"  # 512 MiB RAM max
        livenessProbe:
          httpGet:
            path: /
            port: 4321
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 4321
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Rationale for Values**:
- Server: Flask with SQLAlchemy requires more memory for database connections
- Client: Static-served Astro site with minimal runtime overhead
- Requests set to 50% of limits to allow bursting
- Liveness delay accounts for application startup time

**Alternatives Considered**:
- Higher limits: Rejected to maximize node utilization and reduce costs
- No limits: Violates Constitution Principle IV

**References**:
- Kubernetes resource management documentation
- Flask/Gunicorn production deployment guides

---

### 6. Azure Managed Identity for ACR

**Decision**: Use AKS kubelet managed identity with AcrPull role assignment

**Rationale**:
- Eliminates image pull secrets in Kubernetes (Constitution Principle IV)
- Automatic credential rotation via Azure
- Simpler than service principal credentials
- Native Azure integration reduces attack surface

**Implementation Details**:

**Terraform Configuration** (`infra/modules/rbac/main.tf`):
```hcl
# Get AKS kubelet identity after cluster creation
data "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  resource_group_name = var.resource_group_name
}

# Assign AcrPull role to AKS managed identity
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = data.azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}
```

**Kubernetes Deployment** (no imagePullSecrets required):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tailspin-server
spec:
  template:
    spec:
      containers:
      - name: server
        image: acrtailspin.azurecr.io/tailspin-server:v1.0.0
        # No imagePullSecrets needed - managed identity handles authentication
```

**Alternatives Considered**:
- Image pull secrets: Rejected due to Constitution requirement and manual rotation overhead
- Service principal: Rejected in favor of managed identity

**References**:
- AKS managed identity documentation
- ACR authentication with AKS guide

---

### 7. GitHub Actions Workflow Orchestration

**Decision**: Use three separate workflows with manual/automatic triggers and dependencies

**Rationale**:
- Separation of concerns: infrastructure, containers, application deployment
- Enables independent execution for faster iterations
- Supports infrastructure drift detection without redeploying apps
- Aligns with Constitution deployment validation requirements

**Implementation Details**:

**Workflow 1: Infrastructure Deployment** (`.github/workflows/infra-deploy.yml`):
- **Trigger**: Manual (workflow_dispatch), push to infra/**
- **Purpose**: Provision/update AKS, ACR, networking, monitoring
- **Steps**: Terraform init → validate → plan → apply
- **Outputs**: AKS cluster name, ACR URL (set as job outputs)

**Workflow 2: Docker Build & Scan** (`.github/workflows/docker-build.yml`):
- **Trigger**: Push to server/**, client/**, manual
- **Purpose**: Build, scan, push container images to ACR
- **Steps**: Build image → Trivy scan → Push to ACR
- **Outputs**: Image tags with commit SHA

**Workflow 3: Application Deployment** (`.github/workflows/app-deploy.yml`):
- **Trigger**: Workflow completion (docker-build), manual
- **Purpose**: Deploy applications to AKS cluster
- **Steps**: Get AKS credentials → Update manifests with new image tags → kubectl apply → Smoke tests
- **Dependencies**: Requires docker-build workflow success

**Workflow Dependencies**:
```yaml
# app-deploy.yml
on:
  workflow_run:
    workflows: ["Docker Build & Scan"]
    types: [completed]
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
```

**Alternatives Considered**:
- Single monolithic workflow: Rejected due to long execution time and lack of flexibility
- Matrix builds: Rejected as infrastructure/app deployment are sequential, not parallel

**References**:
- GitHub Actions workflow triggers documentation
- Workflow dependencies and outputs patterns

---

### 8. Rollback Strategies

**Decision**: Implement automated Kubernetes rollback and manual Terraform state restoration

**Rationale**:
- Kubernetes rollback via `kubectl rollout undo` for application failures
- Terraform state backup/restore for infrastructure issues
- Meets Constitution rollback time target (<5 minutes)
- Balances automation with safety (Terraform manual review)

**Implementation Details**:

**Kubernetes Rollback** (automated in app-deploy workflow):
```yaml
- name: Deploy Application
  id: deploy
  run: |
    kubectl apply -f k8s/
    kubectl rollout status deployment/tailspin-server -n tail-spin --timeout=300s
    kubectl rollout status deployment/tailspin-client -n tail-spin --timeout=300s

- name: Run Smoke Tests
  id: smoke-tests
  run: npm run test:e2e:smoke

- name: Rollback on Failure
  if: failure() && steps.deploy.outcome == 'success'
  run: |
    echo "Smoke tests failed - rolling back deployment"
    kubectl rollout undo deployment/tailspin-server -n tail-spin
    kubectl rollout undo deployment/tailspin-client -n tail-spin
    kubectl rollout status deployment/tailspin-server -n tail-spin --timeout=300s
    kubectl rollout status deployment/tailspin-client -n tail-spin --timeout=300s
```

**Terraform Rollback** (manual procedure documented):
```bash
# If infrastructure deployment fails or causes issues:

# 1. List state versions
az storage blob list \
  --account-name sttailspintfstate \
  --container-name tfstate \
  --prefix tailspin-aks.tfstate

# 2. Download previous state
az storage blob download \
  --account-name sttailspintfstate \
  --container-name tfstate \
  --name tailspin-aks.tfstate.<VERSION> \
  --file terraform.tfstate.backup

# 3. Restore state
cp terraform.tfstate.backup infra/terraform.tfstate

# 4. Apply previous configuration
cd infra && terraform apply
```

**Rollback Time Targets**:
- Kubernetes application: <3 minutes (automated)
- Terraform infrastructure: <10 minutes (manual, documented)

**Alternatives Considered**:
- GitOps with ArgoCD: Rejected to reduce initial complexity
- Blue-green deployment: Future enhancement for zero-downtime

**References**:
- Kubernetes rollout management documentation
- Terraform state management best practices

---

## Summary

All technical unknowns have been resolved through research. Key decisions:

1. **Infrastructure**: Terraform with Azure Storage backend, AKS automatic mode, GitHub OIDC authentication
2. **Security**: Trivy vulnerability scanning, managed identities, no secrets in code
3. **Deployment**: Three-phase GitHub Actions workflows with automated rollback
4. **Resource Management**: Conservative Kubernetes limits, health probes for all deployments

No blockers identified. Ready to proceed to Phase 1 (Design & Contracts).
