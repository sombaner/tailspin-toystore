# Troubleshooting Guide

This guide covers common issues encountered during deployment and operations of the Tailspin Toys application on Azure AKS.

## Table of Contents

1. [Infrastructure Issues](#infrastructure-issues)
2. [Container Build Issues](#container-build-issues)
3. [Deployment Issues](#deployment-issues)
4. [Runtime Issues](#runtime-issues)
5. [Networking Issues](#networking-issues)
6. [Authentication Issues](#authentication-issues)

## Infrastructure Issues

### Issue: Terraform Init Fails with "Error building ARM Config"

**Symptoms**:
```
Error: building account: could not acquire access token to parse claims
```

**Causes**:
- GitHub OIDC authentication not configured correctly
- Missing or incorrect GitHub secrets
- Service principal doesn't have required permissions

**Solutions**:

1. Verify GitHub secrets are set correctly:
   ```bash
   # Check in GitHub: Settings → Secrets and variables → Actions
   # Required secrets: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID
   ```

2. Verify federated credentials in Azure AD:
   ```bash
   # List federated credentials
   az ad app federated-credential list --id <app-id>
   
   # Verify subject matches your repository
   # Expected: repo:<org>/<repo>:ref:refs/heads/main
   ```

3. Verify service principal permissions:
   ```bash
   # Check role assignments
   az role assignment list --assignee <app-id> --output table
   
   # Should have "Contributor" role at subscription or resource group scope
   ```

### Issue: Terraform Apply Fails with "Subscription Not Registered"

**Symptoms**:
```
The subscription is not registered to use namespace 'Microsoft.ContainerService'
```

**Solution**:
Register required resource providers:

```bash
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry

# Check registration status
az provider show --namespace Microsoft.ContainerService --query "registrationState"
```

### Issue: AKS Creation Fails with Quota Exceeded

**Symptoms**:
```
QuotaExceeded: Operation could not be completed as it results in exceeding approved standardDSv3Family Cores quota
```

**Solutions**:

1. Request quota increase in Azure Portal:
   - Navigate to **Subscriptions** → **Usage + quotas**
   - Filter by region (Central India) and resource (Compute)
   - Request increase for DSv3 family cores

2. Use smaller VM size temporarily:
   ```hcl
   # In infra/terraform.tfvars
   node_pool_vm_size = "Standard_B2s"  # Smaller size
   ```

3. Use different region with available quota:
   ```hcl
   # In infra/terraform.tfvars
   location = "southeastasia"  # Alternative region
   ```

### Issue: Storage Account Name Already Exists

**Symptoms**:
```
StorageAccountAlreadyTaken: The storage account named 'sttfstateprod' is already taken
```

**Solution**:
Storage account names must be globally unique. Generate a new name:

```bash
# Generate unique storage account name
STORAGE_ACCOUNT_NAME="sttfstateprod$(openssl rand -hex 3)"
echo $STORAGE_ACCOUNT_NAME

# Update infra/backend.tf with the new name
```

## Container Build Issues

### Issue: Trivy Scan Fails with HIGH/CRITICAL Vulnerabilities

**Symptoms**:
```
❌ Security scan failed: HIGH or CRITICAL vulnerabilities detected
```

**Solution**:

1. Review vulnerabilities in GitHub Security tab:
   - Navigate to **Security** → **Code scanning**
   - Filter by alert type: Trivy

2. Update base images to latest patched versions:
   ```dockerfile
   # server/Dockerfile - Update Python base image
   FROM python:3.11-slim  # Change to latest available

   # client/Dockerfile - Update Node base image
   FROM node:lts  # Or specify exact version like node:20-alpine
   ```

3. Update dependencies with security patches:
   ```bash
   # For server (Python)
   cd server
   pip install --upgrade -r requirements.txt
   pip-audit  # Check for vulnerabilities

   # For client (Node)
   cd client
   npm audit fix
   npm update
   ```

4. If vulnerabilities cannot be fixed immediately:
   - Document as known issue
   - Set `continue-on-error: true` temporarily (NOT recommended for production)
   - Create tracking issue for remediation

### Issue: Docker Build Fails with "No Space Left on Device"

**Symptoms**:
```
Error: failed to solve: write /var/lib/docker/...No space left on device
```

**Solution**:

1. Clean up Docker cache in workflow:
   ```yaml
   - name: Clean Docker Cache
     run: docker system prune -af --volumes
   ```

2. Use GitHub's larger runners (if available)

3. Optimize Dockerfile with multi-stage builds:
   ```dockerfile
   # Use build stage and copy only necessary artifacts
   FROM node:lts AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   FROM node:lts-alpine
   WORKDIR /app
   COPY --from=builder /app/dist ./dist
   CMD ["node", "dist/server/entry.mjs"]
   ```

### Issue: ACR Login Fails

**Symptoms**:
```
Error: UNAUTHORIZED: authentication required
```

**Solution**:

1. Verify ACR exists and is accessible:
   ```bash
   az acr list --resource-group rg-sb-aks-01 --output table
   ```

2. Check service principal has AcrPush role:
   ```bash
   ACR_ID=$(az acr show --name <acr-name> --query id -o tsv)
   az role assignment list --scope $ACR_ID --output table
   ```

3. Re-login to ACR:
   ```bash
   az acr login --name <acr-name>
   ```

## Deployment Issues

### Issue: Pods Stuck in ImagePullBackOff

**Symptoms**:
```
kubectl get pods -n tail-spin
NAME                              READY   STATUS             RESTARTS   AGE
tailspin-server-xxx               0/1     ImagePullBackOff   0          2m
```

**Causes**:
- AKS cannot authenticate to ACR
- Image doesn't exist in ACR
- Image tag is incorrect

**Solutions**:

1. Verify AKS to ACR role assignment:
   ```bash
   # Check RBAC module was applied correctly
   cd infra
   terraform state show module.rbac.azurerm_role_assignment.aks_acr_pull
   ```

2. Verify image exists in ACR:
   ```bash
   az acr repository list --name <acr-name> --output table
   az acr repository show-tags --name <acr-name> --repository tailspin-server
   ```

3. Check pod events:
   ```bash
   kubectl describe pod <pod-name> -n tail-spin
   # Look for "Failed to pull image" errors
   ```

4. Manually test ACR authentication from AKS:
   ```bash
   # Exec into a pod
   kubectl run test --image=busybox -n tail-spin --rm -it -- sh

   # Try pulling image (requires docker)
   ```

### Issue: Pods in CrashLoopBackOff

**Symptoms**:
```
kubectl get pods -n tail-spin
NAME                              READY   STATUS             RESTARTS   AGE
tailspin-server-xxx               0/1     CrashLoopBackOff   5          5m
```

**Solution**:

1. Check pod logs for errors:
   ```bash
   kubectl logs <pod-name> -n tail-spin --tail=100
   kubectl logs <pod-name> -n tail-spin --previous  # Logs from crashed container
   ```

2. Common application errors:
   - Missing environment variables
   - Database connection failures
   - Port conflicts
   - Application startup errors

3. Verify environment variables:
   ```bash
   kubectl describe pod <pod-name> -n tail-spin
   # Check "Environment" section
   ```

4. Check resource limits:
   ```bash
   kubectl describe pod <pod-name> -n tail-spin
   # Check if pod is OOMKilled (out of memory)
   ```

5. Adjust resource limits if needed:
   ```yaml
   # In k8s/server-deployment.yaml
   resources:
     limits:
       memory: "2Gi"  # Increase if OOMKilled
   ```

### Issue: LoadBalancer External IP Stuck in Pending

**Symptoms**:
```
kubectl get svc tailspin-client -n tail-spin
NAME              TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
tailspin-client   LoadBalancer   10.0.45.123   <pending>     80:31234/TCP   10m
```

**Causes**:
- Azure Load Balancer provisioning delay
- Quota exceeded for public IP addresses
- Network configuration issues

**Solutions**:

1. Wait longer (can take 5-10 minutes):
   ```bash
   kubectl get svc tailspin-client -n tail-spin --watch
   ```

2. Check service events:
   ```bash
   kubectl describe svc tailspin-client -n tail-spin
   ```

3. Verify public IP quota:
   ```bash
   az vm list-usage --location centralindia --output table | grep "Public IP"
   ```

4. Check AKS node resource group:
   ```bash
   # Get node resource group
   NODE_RG=$(az aks show --resource-group rg-sb-aks-01 --name <aks-name> --query nodeResourceGroup -o tsv)
   
   # List public IPs
   az network public-ip list --resource-group $NODE_RG --output table
   ```

### Issue: Health Checks Failing

**Symptoms**:
```
Readiness probe failed: Get http://10.244.0.15:5100/api/games: dial tcp 10.244.0.15:5100: connect: connection refused
```

**Solutions**:

1. Verify application is listening on correct port:
   ```bash
   kubectl logs <pod-name> -n tail-spin | grep "Listening"
   ```

2. Check readiness probe path is correct:
   ```yaml
   # In deployment manifest
   readinessProbe:
     httpGet:
       path: /api/games  # Verify this endpoint exists
       port: 5100
   ```

3. Increase initial delay:
   ```yaml
   readinessProbe:
     initialDelaySeconds: 30  # Give app more time to start
   ```

4. Test endpoint manually:
   ```bash
   kubectl port-forward pod/<pod-name> 5100:5100 -n tail-spin
   curl http://localhost:5100/api/games
   ```

## Runtime Issues

### Issue: Application Returns 502 Bad Gateway

**Causes**:
- Backend server not responding
- Network connectivity issues
- Service configuration incorrect

**Solutions**:

1. Check if server pods are running:
   ```bash
   kubectl get pods -n tail-spin -l app=tailspin-server
   ```

2. Verify service endpoints:
   ```bash
   kubectl get endpoints tailspin-server -n tail-spin
   # Should show pod IPs
   ```

3. Test server connectivity from client pod:
   ```bash
   # Exec into client pod
   kubectl exec -it <client-pod> -n tail-spin -- sh
   
   # Test server endpoint
   curl http://tailspin-server.tail-spin.svc.cluster.local:5100/api/games
   ```

4. Check API_SERVER_URL environment variable in client:
   ```bash
   kubectl describe pod <client-pod> -n tail-spin | grep API_SERVER_URL
   ```

### Issue: Database Connection Errors

**Symptoms**:
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Cause**:
SQLite database file not present in container

**Solution**:

1. Verify database is copied in Dockerfile:
   ```dockerfile
   # server/Dockerfile
   COPY data/tailspin-toys.db /app/data/tailspin-toys.db
   ```

2. Check database file in pod:
   ```bash
   kubectl exec -it <server-pod> -n tail-spin -- ls -la /app/data/
   ```

3. For persistent database, use PersistentVolumeClaim:
   ```yaml
   # Create PVC for database (if needed)
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: server-data
   spec:
     accessModes: [ReadWriteOnce]
     resources:
       requests:
         storage: 1Gi
   ```

## Networking Issues

### Issue: Cannot Access Application from Internet

**Solutions**:

1. Verify external IP is assigned:
   ```bash
   kubectl get svc tailspin-client -n tail-spin
   ```

2. Check if port 80 is accessible:
   ```bash
   EXTERNAL_IP=$(kubectl get svc tailspin-client -n tail-spin -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
   curl -v http://$EXTERNAL_IP
   ```

3. Verify Azure NSG rules (if custom networking):
   ```bash
   # Check NSG associated with AKS subnet
   az network nsg list --resource-group <node-resource-group> --output table
   ```

4. Test from Azure Cloud Shell:
   ```bash
   # Open Azure Cloud Shell
   curl http://<external-ip>
   ```

### Issue: Pod-to-Pod Communication Fails

**Solutions**:

1. Test DNS resolution:
   ```bash
   kubectl run test --image=busybox -n tail-spin --rm -it -- nslookup tailspin-server.tail-spin.svc.cluster.local
   ```

2. Verify network policies (if enabled):
   ```bash
   kubectl get networkpolicies -n tail-spin
   ```

3. Check cluster DNS:
   ```bash
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   ```

## Authentication Issues

### Issue: GitHub Actions Workflow Fails with Authentication Error

**Symptoms**:
```
Error: AADSTS700016: Application with identifier '<client-id>' was not found
```

**Solution**:

1. Verify Azure AD application exists:
   ```bash
   az ad app show --id <client-id>
   ```

2. Check federated credentials:
   ```bash
   az ad app federated-credential list --id <client-id>
   ```

3. Verify GitHub secrets match Azure values:
   - `AZURE_CLIENT_ID` = Application (client) ID
   - `AZURE_TENANT_ID` = Directory (tenant) ID
   - `AZURE_SUBSCRIPTION_ID` = Subscription ID

4. Re-create federated credential if needed:
   ```bash
   az ad app federated-credential delete --id <app-id> --federated-credential-id <cred-id>
   
   az ad app federated-credential create --id <app-id> --parameters '{
     "name": "github-actions-main",
     "issuer": "https://token.actions.githubusercontent.com",
     "subject": "repo:<org>/<repo>:ref:refs/heads/main",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

### Issue: OIDC Authentication Fails with "No matching federated identity record found"

**Symptoms**:
```
Error: AADSTS700213: No matching federated identity record found for presented assertion subject 
'repo:<org>/<repo>:environment:production'. Check your federated identity credential Subject, 
Audience and Issuer against the presented assertion.
```

**Cause**:
The workflow uses `environment: production` (or another environment), but Azure doesn't have a federated credential configured for that environment subject claim.

**Solution Option 1 (Recommended)**: Remove environment designation from workflow

If you don't need GitHub Environment approval gates, remove the `environment:` line from your workflow:

```yaml
# Before:
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Remove this line
    steps: ...

# After:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps: ...
```

This changes the subject claim from `environment:production` to `ref:refs/heads/main`, matching the standard federated credential.

**Solution Option 2**: Add environment-specific federated credential in Azure

If you need GitHub Environments for approval gates or environment-specific secrets, add a federated credential for each environment:

```bash
# For production environment
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "github-actions-production",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:<org>/<repo>:environment:production",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# For staging environment (if needed)
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "github-actions-staging",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:<org>/<repo>:environment:staging",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Verification**:

List all federated credentials to verify configuration:
```bash
az ad app federated-credential list --id <app-id> --query "[].{name:name, subject:subject}" -o table
```

## Getting Help

If issues persist:

1. **Check Logs**:
   - GitHub Actions workflow logs
   - Kubernetes pod logs: `kubectl logs <pod> -n tail-spin`
   - Azure Monitor logs in Azure Portal

2. **Create GitHub Issue**:
   - Include workflow run ID
   - Attach relevant log snippets
   - Describe steps to reproduce

3. **Azure Support**:
   - For Azure-specific issues, open support ticket in Azure Portal
   - Include subscription ID and resource details

## Useful Commands Reference

```bash
# Infrastructure
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply

# Azure
az aks list --output table
az acr repository list --name <acr-name>
az aks get-credentials --resource-group <rg> --name <aks-name>

# Kubernetes
kubectl get all -n tail-spin
kubectl describe pod <pod-name> -n tail-spin
kubectl logs <pod-name> -n tail-spin --tail=100 -f
kubectl rollout restart deployment/tailspin-server -n tail-spin
kubectl port-forward svc/tailspin-client 8080:80 -n tail-spin

# Debugging
kubectl run debug --image=busybox -n tail-spin --rm -it -- sh
kubectl exec -it <pod-name> -n tail-spin -- /bin/sh
```
