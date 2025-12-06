# Quickstart: AKS Deployment Automation

**Feature**: 001-aks-deployment-automation  
**Last Updated**: 2025-12-07  
**Estimated Time**: 45 minutes (first-time setup)

## Overview

This guide walks through deploying the Tailspin application to Azure Kubernetes Service (AKS) using automated GitHub Actions workflows. The deployment consists of three phases:

1. **Infrastructure Provisioning**: Terraform creates AKS cluster, ACR, networking, and monitoring
2. **Container Build & Scan**: Docker images are built, scanned for vulnerabilities, and pushed to ACR
3. **Application Deployment**: Kubernetes manifests deploy Tailspin server and client to AKS

---

## Prerequisites

### Azure Requirements

- [ ] Azure subscription with sufficient quota for AKS and ACR in Central India region
- [ ] Contributor role on the subscription
- [ ] Azure CLI installed locally (for one-time setup)

### GitHub Requirements

- [ ] GitHub repository with Actions enabled
- [ ] Repository permissions to configure secrets and environments

### Local Development (Optional)

- [ ] Terraform CLI 1.6+ (for local testing)
- [ ] kubectl 1.28+ (for cluster interaction)
- [ ] Docker 24.0+ (for local image builds)

---

## One-Time Setup

### Step 1: Configure Azure AD Application for GitHub OIDC

**Purpose**: Enable GitHub Actions to authenticate to Azure without storing credentials.

```bash
# Login to Azure
az login
az account set --subscription <SUBSCRIPTION_ID>

# Create Azure AD Application
APP_ID=$(az ad app create --display-name "github-actions-tailspin" --query appId -o tsv)
echo "Application (Client) ID: $APP_ID"

# Create Service Principal
az ad sp create --id $APP_ID

# Create Federated Credential for GitHub
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-tailspin-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:github-samples/agents-in-sdlc:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Assign Contributor role
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope /subscriptions/$SUBSCRIPTION_ID

# Get Tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "Tenant ID: $TENANT_ID"
echo "Subscription ID: $SUBSCRIPTION_ID"
```

**Save these values** for GitHub Secrets:
- `AZURE_CLIENT_ID`: Application (Client) ID
- `AZURE_TENANT_ID`: Tenant ID
- `AZURE_SUBSCRIPTION_ID`: Subscription ID

---

### Step 2: Create Azure Storage for Terraform State

**Purpose**: Store Terraform state remotely for team collaboration and state locking.

```bash
# Set variables
RESOURCE_GROUP="rg-sb-aks-01"
LOCATION="centralindia"
STORAGE_ACCOUNT="sttailspintfstate"  # Must be globally unique - adjust if taken
CONTAINER_NAME="tfstate"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --encryption-services blob \
  --min-tls-version TLS1_2

# Create blob container
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --auth-mode login

echo "✅ Terraform state backend ready"
echo "   Storage Account: $STORAGE_ACCOUNT"
echo "   Container: $CONTAINER_NAME"
```

---

### Step 3: Configure GitHub Secrets

Navigate to your repository: **Settings → Secrets and variables → Actions**

**Add Repository Secrets**:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `AZURE_CLIENT_ID` | Application (Client) ID | From Step 1 |
| `AZURE_TENANT_ID` | Tenant ID | From Step 1 |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | From Step 1 |

**Verify Setup**:
```bash
# In GitHub Actions workflow, test authentication
- name: Azure Login
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

---

## Deployment Workflow

### Phase 1: Infrastructure Provisioning

**Workflow**: `.github/workflows/infra-deploy.yml`

1. **Trigger the workflow**:
   - Go to **Actions → Infrastructure Deploy → Run workflow**
   - Select branch: `001-aks-deployment-automation`
   - Click **Run workflow**

2. **Monitor progress** (12-15 minutes):
   ```
   ✅ Checkout code
   ✅ Azure Login (OIDC)
   ✅ Terraform Init
   ✅ Terraform Validate
   ✅ Terraform Plan (review output)
   ✅ Terraform Apply
      - Creating resource group
      - Creating virtual network and subnet
      - Provisioning AKS cluster (longest step: ~10 min)
      - Creating Azure Container Registry
      - Creating Log Analytics & Application Insights
      - Configuring RBAC (AKS → ACR)
   ✅ Output cluster details
   ```

3. **Verify infrastructure**:
   ```bash
   # Get AKS credentials
   az aks get-credentials \
     --resource-group rg-sb-aks-01 \
     --name aks-tailspin-prod \
     --overwrite-existing
   
   # Check cluster status
   kubectl cluster-info
   kubectl get nodes
   # Expected: 1-3 nodes in Ready state
   
   # Verify ACR
   az acr show --name acrtailspin --resource-group rg-sb-aks-01 --query "loginServer" -o tsv
   # Expected: acrtailspin.azurecr.io
   ```

**Troubleshooting**:

- **Error: "Subscription not registered"**
  ```bash
  az provider register --namespace Microsoft.ContainerService
  az provider register --namespace Microsoft.ContainerRegistry
  # Wait 5-10 minutes for registration
  ```

- **Error: "Quota exceeded"**
  ```bash
  az vm list-usage --location centralindia --query "[?name.value=='standardDSv2Family'].{Name:name.value, CurrentValue:currentValue, Limit:limit}" -o table
  # Request quota increase in Azure Portal
  ```

---

### Phase 2: Container Build & Scan

**Workflow**: `.github/workflows/docker-build.yml`

1. **Trigger the workflow**:
   - Automatically triggered after infrastructure deploy
   - Or manually: **Actions → Docker Build & Scan → Run workflow**

2. **Monitor progress** (8-12 minutes total):
   
   **Server Image**:
   ```
   ✅ Checkout code
   ✅ Build server Docker image (server/Dockerfile)
   ✅ Scan with Trivy (check for vulnerabilities)
   ✅ Azure Login
   ✅ Push to ACR: acrtailspin.azurecr.io/tailspin-server:abc123f
   ```
   
   **Client Image**:
   ```
   ✅ Checkout code
   ✅ Build client Docker image (client/Dockerfile)
   ✅ Scan with Trivy (check for vulnerabilities)
   ✅ Azure Login
   ✅ Push to ACR: acrtailspin.azurecr.io/tailspin-client:abc123f
   ```

3. **Verify images in ACR**:
   ```bash
   # List repositories
   az acr repository list --name acrtailspin -o table
   # Expected: tailspin-client, tailspin-server
   
   # List tags for server
   az acr repository show-tags --name acrtailspin --repository tailspin-server -o table
   
   # List tags for client
   az acr repository show-tags --name acrtailspin --repository tailspin-client -o table
   ```

**Handling Vulnerabilities**:

- **HIGH/CRITICAL vulnerabilities**: Pipeline will fail
  - Review Trivy output in GitHub Actions logs
  - Update base images or dependencies in Dockerfile
  - Re-run workflow after fixes

- **MEDIUM/LOW vulnerabilities**: Pipeline continues
  - Monitor trends over time
  - Plan updates during maintenance windows

---

### Phase 3: Application Deployment

**Workflow**: `.github/workflows/app-deploy.yml`

1. **Trigger the workflow**:
   - Automatically triggered after successful container build
   - Or manually: **Actions → Application Deployment → Run workflow**

2. **Monitor progress** (3-5 minutes):
   ```
   ✅ Checkout code
   ✅ Azure Login
   ✅ Get AKS credentials
   ✅ Create namespace: tail-spin
   ✅ Update image tags in manifests
   ✅ Deploy server: kubectl apply -f k8s/server-deployment.yaml
   ✅ Deploy client: kubectl apply -f k8s/client-deployment.yaml
   ✅ Create LoadBalancer: kubectl apply -f k8s/client-service.yaml
   ✅ Wait for rollout completion
   ✅ Run smoke tests (Playwright)
   ```

3. **Get external IP address**:
   ```bash
   kubectl get service tailspin-client-lb -n tail-spin
   # Wait for EXTERNAL-IP to show (not <pending>)
   ```
   
   Output:
   ```
   NAME                  TYPE           EXTERNAL-IP      PORT(S)        AGE
   tailspin-client-lb    LoadBalancer   20.235.123.45    80:30123/TCP   2m
   ```

4. **Access the application**:
   ```bash
   # Open in browser
   open http://20.235.123.45
   
   # Or use curl
   curl -I http://20.235.123.45
   # Expected: HTTP/1.1 200 OK
   ```

5. **Verify pods and services**:
   ```bash
   # Check pod status
   kubectl get pods -n tail-spin
   # Expected: All pods Running with 2/2 READY
   
   # Check logs
   kubectl logs -n tail-spin deployment/tailspin-server --tail=50
   kubectl logs -n tail-spin deployment/tailspin-client --tail=50
   
   # Check resource usage
   kubectl top pods -n tail-spin
   ```

**Troubleshooting**:

- **Pods stuck in ImagePullBackOff**:
  ```bash
  # Check ACR access
  kubectl describe pod <POD_NAME> -n tail-spin
  # Look for "unauthorized" or "authentication required"
  
  # Verify RBAC role assignment
  az role assignment list --scope $(az acr show -n acrtailspin --query id -o tsv)
  ```

- **Pods CrashLoopBackOff**:
  ```bash
  # Check pod logs
  kubectl logs <POD_NAME> -n tail-spin --previous
  
  # Check liveness/readiness probe endpoints
  kubectl describe pod <POD_NAME> -n tail-spin
  ```

- **Service external IP stuck in <pending>**:
  ```bash
  # Check Azure Load Balancer provisioning
  kubectl describe service tailspin-client-lb -n tail-spin
  
  # May take 3-5 minutes for Azure to provision public IP
  ```

---

## Post-Deployment Validation

### Health Checks

```bash
# Server health endpoint
SERVER_IP=$(kubectl get pods -n tail-spin -l app=tailspin-server -o jsonpath='{.items[0].status.podIP}')
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://$SERVER_IP:5000/health

# Client health endpoint
CLIENT_IP=$(kubectl get service tailspin-client-lb -n tail-spin -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$CLIENT_IP/
```

### E2E Tests

```bash
# Run full E2E test suite
cd tests/e2e
export BASE_URL=http://$CLIENT_IP
npm run test:e2e
```

### Monitoring

```bash
# View logs in Azure Portal
echo "Log Analytics Workspace: log-tailspin-prod"
echo "Resource Group: rg-sb-aks-01"

# Query logs
az monitor log-analytics query \
  --workspace <WORKSPACE_ID> \
  --analytics-query "ContainerLog | where TimeGenerated > ago(1h) | limit 50" \
  --output table
```

---

## Rollback Procedure

### Application Rollback (Automated)

If smoke tests fail, the workflow automatically rolls back:

```yaml
# In app-deploy.yml
- name: Rollback on Failure
  if: failure()
  run: |
    kubectl rollout undo deployment/tailspin-server -n tail-spin
    kubectl rollout undo deployment/tailspin-client -n tail-spin
```

### Manual Rollback

```bash
# Check rollout history
kubectl rollout history deployment/tailspin-server -n tail-spin

# Rollback to previous version
kubectl rollout undo deployment/tailspin-server -n tail-spin
kubectl rollout undo deployment/tailspin-client -n tail-spin

# Rollback to specific revision
kubectl rollout undo deployment/tailspin-server -n tail-spin --to-revision=2
```

### Infrastructure Rollback

```bash
# Restore previous Terraform state
cd infra
terraform state pull > current-state.json

# Download previous state from Azure Storage
az storage blob download \
  --account-name sttailspintfstate \
  --container-name tfstate \
  --name tailspin-aks.tfstate.backup \
  --file terraform.tfstate

# Apply previous configuration
terraform plan  # Review changes
terraform apply
```

---

## Cleanup

### Delete Application

```bash
kubectl delete namespace tail-spin
```

### Delete Infrastructure

```bash
cd infra
terraform destroy -auto-approve

# Or via Azure CLI
az group delete --name rg-sb-aks-01 --yes --no-wait
```

---

## Common Operations

### Update Application Code

1. Commit code changes to repository
2. GitHub Actions automatically triggers docker-build workflow
3. New images built and pushed to ACR
4. app-deploy workflow triggers and updates Kubernetes deployments
5. Verify deployment: `kubectl rollout status deployment/tailspin-server -n tail-spin`

### Scale Deployment

```bash
# Scale server replicas
kubectl scale deployment tailspin-server -n tail-spin --replicas=3

# Scale client replicas
kubectl scale deployment tailspin-client -n tail-spin --replicas=3

# Verify scaling
kubectl get pods -n tail-spin -w
```

### Update Resource Limits

Edit `k8s/server-deployment.yaml` or `k8s/client-deployment.yaml`:

```yaml
resources:
  requests:
    cpu: "500m"       # Increased from 250m
    memory: "1Gi"     # Increased from 512Mi
  limits:
    cpu: "2000m"
    memory: "2Gi"
```

Apply changes:
```bash
kubectl apply -f k8s/server-deployment.yaml
kubectl rollout restart deployment/tailspin-server -n tail-spin
```

---

## Next Steps

1. **Configure Custom Domain**: Map LoadBalancer IP to DNS record
2. **Enable HTTPS**: Install cert-manager and configure Ingress with TLS
3. **Set Up Multi-Environment**: Extend Terraform for dev/staging/prod
4. **Implement HPA**: Add Horizontal Pod Autoscaler for automatic scaling
5. **Configure Alerts**: Set up Azure Monitor alerts for production monitoring

---

## Support & Documentation

- **Spec**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Module Contracts**: [contracts/](./contracts/)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

For issues or questions, open a GitHub issue in the repository.
