# AKS Deployment Instructions

This document explains how to deploy the Tailspin Toystore application to Azure Kubernetes Service (AKS) using GitHub Actions.

## Prerequisites

1. **Azure Resources**: Ensure you have the following Azure resources created:
   - AKS Cluster: `sbAKSCluster` in resource group `sb-aks-rg`
   - Proper OIDC authentication configured between GitHub and Azure

2. **GitHub Secrets**: Configure the following secrets in your GitHub repository:
   - `AZURE_CLIENT_ID`: Azure application client ID for OIDC authentication
   - `AZURE_TENANT_ID`: Azure tenant ID
   - `AZURE_SUBSCRIPTION_ID`: Azure subscription ID

3. **GitHub Container Registry Packages**: Make the following packages public:
   - `tailspin-toystore/tailspin-client`
   - `tailspin-toystore/tailspin-server`

## Making Container Packages Public

After the first workflow run that builds and pushes images, you need to make the packages public:

1. Go to your GitHub repository
2. Click on "Packages" in the right sidebar
3. Click on each package (`tailspin-client` and `tailspin-server`)
4. Click "Package settings" in the right sidebar
5. Scroll down to "Danger Zone"
6. Click "Change visibility"
7. Select "Public"
8. Confirm the change

## Deployment Process

### Automatic Deployment

The workflows are configured to trigger automatically when:
- Changes are pushed to the `main` branch that affect:
  - `client/**` or `k8s/client-deployment.yaml` for client deployment
  - `server/**` or `k8s/server-deployment.yaml` for server deployment

### Manual Deployment

You can also trigger deployments manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select either "Build and Deploy Client to AKS" or "Build and Deploy Server to AKS"
3. Click "Run workflow"
4. Select the `main` branch
5. Click "Run workflow"

## Verifying Deployment

After the workflows complete successfully:

### Check Client Service

The client service is exposed via a LoadBalancer. To get the URL:

```bash
kubectl -n tail-spin get svc tailspin-client
```

Look for the `EXTERNAL-IP` column. The client application URL will be:
```
http://<EXTERNAL-IP>
```

### Check Server Service

The server service is internal (ClusterIP). To verify:

```bash
kubectl -n tail-spin get svc tailspin-server
```

### Check Pods Status

```bash
kubectl -n tail-spin get pods
```

All pods should be in `Running` state.

## Architecture

- **Client**: Astro/Svelte frontend running on port 4321
- **Server**: Flask backend API running on port 5100
- **Communication**: Client connects to server via internal Kubernetes DNS: `http://tailspin-server.tail-spin.svc.cluster.local:5100`

## Image Configuration

The deployment uses the following container images from GitHub Container Registry:

- Client: `ghcr.io/sombaner/tailspin-toystore/tailspin-client:latest`
- Server: `ghcr.io/sombaner/tailspin-toystore/tailspin-server:latest`

Images are tagged with both `latest` and the commit SHA for traceability.

## Troubleshooting

### Pods in ImagePullBackOff state

If pods cannot pull images:
1. Verify packages are set to public visibility in GitHub
2. Check that the image names in deployment YAML match the ones in workflows
3. Verify the images exist in GHCR: `https://github.com/sombaner/tailspin-toystore/pkgs/container/tailspin-toystore%2Ftailspin-client`

### LoadBalancer External IP shows <pending>

If the client service doesn't get an external IP:
1. Check AKS cluster has proper networking configuration
2. Verify Azure subscription has available public IPs
3. Check Azure Load Balancer service in the AKS cluster's resource group

### Workflow Authentication Failures

If workflows fail to authenticate with Azure:
1. Verify OIDC federation is properly configured
2. Check that all three Azure secrets are set correctly
3. Ensure the Azure application has proper permissions on the AKS cluster

## Monitoring

Once deployed, the application includes:
- Readiness probes: Ensure pods are ready to receive traffic
- Liveness probes: Restart pods if they become unhealthy
- Resource limits: Prevent resource exhaustion

Check pod health:
```bash
kubectl -n tail-spin describe pod <pod-name>
```

View pod logs:
```bash
kubectl -n tail-spin logs <pod-name>
```
