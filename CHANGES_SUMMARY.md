# Summary of Changes - AKS Deployment Image Name Fix

## Changes Made

### 1. Updated Kubernetes Deployment Files

**k8s/client-deployment.yaml**
- Changed image from: `ACR_LOGIN_SERVER/tailspin-client:latest`
- Changed image to: `ghcr.io/OWNER/REPO/tailspin-client:latest`

**k8s/server-deployment.yaml**
- Changed image from: `ACR_LOGIN_SERVER/tailspin-server:latest`
- Changed image to: `ghcr.io/OWNER/REPO/tailspin-server:latest`

These placeholder patterns (`OWNER/REPO`) are replaced during workflow execution with the actual repository name (`sombaner/tailspin-toystore`) and specific commit SHA.

### 2. Updated GitHub Actions Workflows

**client-deploy-aks.yml and server-deploy-aks.yml**
- Removed the imagePullSecrets creation steps (lines that created `ghcr-creds` secret)
- Removed dependency on `GHCR_USERNAME` and `GHCR_TOKEN` secrets
- Simplified namespace creation to not include Docker registry authentication

This allows the deployments to work with public container images without requiring authentication.

### 3. Added Documentation

**DEPLOYMENT_INSTRUCTIONS.md**
- Comprehensive guide for deploying to AKS
- Instructions for making container packages public
- Troubleshooting guide
- Architecture overview

## How It Works

The deployment process now works as follows:

1. **Build Job**:
   - Builds Docker image for client or server
   - Pushes to GHCR as `ghcr.io/sombaner/tailspin-toystore/tailspin-client:latest` and `ghcr.io/sombaner/tailspin-toystore/tailspin-client:<commit-sha>`
   - Uses sed to replace `ghcr.io/OWNER/REPO/tailspin-client:latest` with the actual image name and commit SHA
   - Creates rendered YAML file with the specific image tag

2. **Deploy Job**:
   - Authenticates with Azure using OIDC
   - Gets AKS credentials
   - Creates namespace if it doesn't exist
   - Applies the deployment with the rendered YAML (containing the specific commit SHA tag)
   - Waits for rollout to complete

## Next Steps for User

### Step 1: Merge This PR

Merge this pull request to the `main` branch. This will automatically trigger both workflows because:
- `k8s/client-deployment.yaml` was modified (triggers client deployment)
- `k8s/server-deployment.yaml` was modified (triggers server deployment)

### Step 2: Make Container Packages Public

After the first workflow run completes and images are pushed to GHCR:

1. Go to https://github.com/sombaner/tailspin-toystore
2. Click "Packages" in the right sidebar
3. For each package (`tailspin-client` and `tailspin-server`):
   - Click on the package name
   - Click "Package settings"
   - Scroll to "Danger Zone"
   - Click "Change visibility"
   - Select "Public"
   - Confirm

**Note**: If the workflows fail before you make the packages public, that's expected. Once you make them public, you can re-run the failed workflows or make a small change to trigger them again.

### Step 3: Get the Client Application URL

After successful deployment:

1. Open your terminal with Azure CLI and kubectl configured
2. Connect to your AKS cluster:
   ```bash
   az aks get-credentials --resource-group sb-aks-rg --name sbAKSCluster
   ```
3. Get the client service external IP:
   ```bash
   kubectl -n tail-spin get svc tailspin-client
   ```
4. Look for the `EXTERNAL-IP` column
5. Access the application at: `http://<EXTERNAL-IP>`

Alternatively, you can check the GitHub Actions workflow logs for the "Get client service external IP" step.

### Step 4: Verify Deployment

Check that all pods are running:
```bash
kubectl -n tail-spin get pods
```

Expected output should show both client and server pods in `Running` state:
```
NAME                               READY   STATUS    RESTARTS   AGE
tailspin-client-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
tailspin-server-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

## Verification Checklist

- [ ] PR merged to main branch
- [ ] Client workflow completed successfully
- [ ] Server workflow completed successfully
- [ ] Container packages set to public visibility
- [ ] Both pods are running in AKS
- [ ] Client LoadBalancer has external IP assigned
- [ ] Application is accessible via browser at http://<EXTERNAL-IP>

## If Something Goes Wrong

See the troubleshooting section in DEPLOYMENT_INSTRUCTIONS.md for common issues and solutions.
