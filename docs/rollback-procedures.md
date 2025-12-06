# Rollback Procedures

This guide provides step-by-step procedures for rolling back deployments in case of failures or issues.

## Table of Contents

1. [Overview](#overview)
2. [Kubernetes Application Rollback](#kubernetes-application-rollback)
3. [Container Image Rollback](#container-image-rollback)
4. [Terraform Infrastructure Rollback](#terraform-infrastructure-rollback)
5. [Emergency Procedures](#emergency-procedures)

## Overview

Rollback strategies by deployment layer:

| Layer | Rollback Method | Time to Rollback | Risk Level |
|-------|----------------|------------------|------------|
| Application (K8s) | `kubectl rollout undo` | < 2 minutes | Low |
| Container Images | Re-deploy previous tag | < 5 minutes | Low |
| Infrastructure (Terraform) | `terraform apply` previous state | 10-15 minutes | Medium |
| Complete System | Full restore from backup | 20-30 minutes | High |

### Rollback Decision Tree

```
Issue Detected
    │
    ├─> Application Error (500, crashes)
    │   └─> Rollback Kubernetes Deployment
    │
    ├─> Container Vulnerability
    │   └─> Rollback to Previous Image Tag
    │
    ├─> Infrastructure Issue (network, cluster)
    │   └─> Rollback Terraform Changes
    │
    └─> Complete System Failure
        └─> Emergency Full Restore
```

## Kubernetes Application Rollback

### Automatic Rollback

The `app-deploy.yml` workflow includes automatic rollback on failure:
- Health check failures trigger rollback
- Smoke test failures trigger rollback
- Deployment timeout triggers rollback

**No manual intervention required** for automatic rollback scenarios.

### Manual Rollback Procedure

**When to Use**: 
- Application issues discovered after deployment
- Performance degradation
- User-reported bugs in production

#### Step 1: Check Rollout History

```bash
# View deployment history for server
kubectl rollout history deployment/tailspin-server -n tail-spin

# View deployment history for client
kubectl rollout history deployment/tailspin-client -n tail-spin

# View specific revision details
kubectl rollout history deployment/tailspin-server -n tail-spin --revision=2
```

**Expected Output**:
```
REVISION  CHANGE-CAUSE
1         Initial deployment
2         Update to v1.1.0
3         Update to v1.2.0 (current)
```

#### Step 2: Rollback to Previous Revision

```bash
# Rollback server to previous revision
kubectl rollout undo deployment/tailspin-server -n tail-spin

# Rollback client to previous revision
kubectl rollout undo deployment/tailspin-client -n tail-spin

# Or rollback to specific revision
kubectl rollout undo deployment/tailspin-server -n tail-spin --to-revision=2
```

#### Step 3: Verify Rollback Status

```bash
# Check rollout status
kubectl rollout status deployment/tailspin-server -n tail-spin
kubectl rollout status deployment/tailspin-client -n tail-spin

# Verify pods are running
kubectl get pods -n tail-spin

# Check pod logs
kubectl logs -n tail-spin -l app=tailspin-server --tail=50
kubectl logs -n tail-spin -l app=tailspin-client --tail=50
```

**Expected Output**:
```
deployment "tailspin-server" successfully rolled out
deployment "tailspin-client" successfully rolled out
```

#### Step 4: Verify Application Functionality

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc tailspin-client -n tail-spin -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test application
curl -I http://$EXTERNAL_IP

# Open in browser
echo "Application URL: http://$EXTERNAL_IP"
```

#### Step 5: Document Rollback

Create GitHub issue documenting:
- Reason for rollback
- Revision rolled back from/to
- Impact duration
- Root cause (if known)
- Prevention measures

### Rollback Time Targets

- **Detection to Decision**: < 5 minutes
- **Execution**: < 2 minutes
- **Verification**: < 3 minutes
- **Total**: < 10 minutes

## Container Image Rollback

### When to Use

- Vulnerabilities discovered in current image
- Need to revert to specific tested version
- Container build issue affecting runtime

### Procedure

#### Step 1: Identify Previous Image Tag

```bash
# List available image tags in ACR
az acr repository show-tags \
  --name <acr-name> \
  --repository tailspin-server \
  --output table

az acr repository show-tags \
  --name <acr-name> \
  --repository tailspin-client \
  --output table
```

**Expected Output**:
```
Result
---------
1.0.0
abc123f
def456g (current)
latest
```

#### Step 2: Update Deployment with Previous Tag

**Option A: Using kubectl set image**

```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr list --resource-group rg-sb-aks-01 --query "[0].loginServer" -o tsv)

# Update server image
kubectl set image deployment/tailspin-server \
  server=$ACR_LOGIN_SERVER/tailspin-server:abc123f \
  -n tail-spin

# Update client image
kubectl set image deployment/tailspin-client \
  client=$ACR_LOGIN_SERVER/tailspin-client:abc123f \
  -n tail-spin
```

**Option B: Edit deployment manifest**

```bash
# Edit deployment
kubectl edit deployment tailspin-server -n tail-spin

# Change image tag under spec.template.spec.containers[0].image
# Save and exit
```

**Option C: Re-run workflow with specific tag**

Update workflow to use specific image tag and re-deploy.

#### Step 3: Monitor Rollout

```bash
# Watch rollout progress
kubectl rollout status deployment/tailspin-server -n tail-spin --watch
kubectl rollout status deployment/tailspin-client -n tail-spin --watch

# Verify pods using correct image
kubectl describe pod <pod-name> -n tail-spin | grep Image
```

## Terraform Infrastructure Rollback

### When to Use

- Infrastructure changes causing cluster issues
- Need to revert networking or monitoring changes
- Resource misconfiguration

**⚠️ WARNING**: Infrastructure rollback is more complex and may cause service disruption.

### Procedure

#### Step 1: Identify State to Restore

```bash
cd infra/

# List state file versions in Azure Storage
az storage blob list \
  --account-name <storage-account-name> \
  --container-name tfstate \
  --prefix tailspin-aks.tfstate \
  --query "[].{Name:name, LastModified:properties.lastModified}" \
  --output table
```

**Note**: Azure Storage versioning must be enabled (configured in setup).

#### Step 2: Review Previous State

```bash
# Download previous state version (if needed)
az storage blob download \
  --account-name <storage-account-name> \
  --container-name tfstate \
  --name tailspin-aks.tfstate \
  --version-id <version-id> \
  --file terraform.tfstate.backup

# Review differences
terraform show terraform.tfstate.backup
```

#### Step 3: Rollback Using Git

**Recommended Approach**: Revert infrastructure code to previous commit

```bash
# View git history
git log --oneline infra/

# Revert to specific commit
git revert <commit-hash>

# Or create new commit with old code
git checkout <commit-hash> -- infra/
git commit -m "Rollback infrastructure to previous version"
```

#### Step 4: Apply Previous Configuration

```bash
# Plan changes
terraform plan

# Review plan carefully - ensure it's reverting desired changes

# Apply rollback
terraform apply

# WARNING: This may recreate resources or cause downtime
# Consider maintenance window for infrastructure rollback
```

#### Step 5: Verify Infrastructure

```bash
# Verify AKS cluster health
az aks show --resource-group rg-sb-aks-01 --name <aks-name> --query provisioningState

# Check cluster connectivity
kubectl cluster-info
kubectl get nodes

# Verify ACR accessibility
az acr check-health --name <acr-name>
```

### Infrastructure Rollback Risks

- **Resource Recreation**: Some resources may be destroyed and recreated
- **Downtime**: Application pods may restart during infrastructure changes
- **State Corruption**: Manual state modifications can break Terraform tracking
- **Cost**: Recreated resources may incur charges

**Best Practice**: Test infrastructure changes in dev/staging environment first.

## Emergency Procedures

### Scenario 1: Complete Cluster Failure

**Symptoms**: 
- Cluster unresponsive
- Cannot connect with kubectl
- Azure Portal shows cluster degraded

**Procedure**:

1. **Assess Cluster Status**:
   ```bash
   az aks show --resource-group rg-sb-aks-01 --name <aks-name> --query powerState
   ```

2. **Start Cluster** (if stopped):
   ```bash
   az aks start --resource-group rg-sb-aks-01 --name <aks-name>
   ```

3. **If cluster is corrupted**, redeploy infrastructure:
   ```bash
   # Destroy and recreate cluster
   cd infra/
   terraform destroy -target=module.aks
   terraform apply -target=module.aks
   ```

4. **Redeploy applications**:
   - Trigger Container Build workflow
   - Trigger Application Deployment workflow

**Recovery Time**: 20-30 minutes

### Scenario 2: ACR Authentication Failure

**Symptoms**:
- All pods in ImagePullBackOff
- Cannot pull images from ACR

**Procedure**:

1. **Verify ACR Status**:
   ```bash
   az acr check-health --name <acr-name>
   ```

2. **Recreate RBAC Assignment**:
   ```bash
   cd infra/
   terraform destroy -target=module.rbac
   terraform apply -target=module.rbac
   ```

3. **Restart Deployments**:
   ```bash
   kubectl rollout restart deployment/tailspin-server -n tail-spin
   kubectl rollout restart deployment/tailspin-client -n tail-spin
   ```

**Recovery Time**: 5-10 minutes

### Scenario 3: Data Loss / Database Corruption

**Symptoms**:
- Application errors reading database
- SQLite file corrupted

**Procedure**:

1. **If using ephemeral database** (current setup):
   ```bash
   # Rebuild and redeploy server image (database is in image)
   # Trigger Container Build workflow
   ```

2. **For persistent database** (future enhancement):
   - Restore from PersistentVolume snapshot
   - Restore from Azure Backup
   - Restore from application-level backup

**Recovery Time**: Depends on backup strategy

### Scenario 4: Workflow Permissions Issue

**Symptoms**:
- GitHub Actions failing with permission errors
- OIDC authentication failures

**Procedure**:

1. **Verify GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Verify AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID

2. **Recreate Federated Credentials**:
   ```bash
   az ad app federated-credential delete --id <app-id> --federated-credential-id <cred-id>
   
   az ad app federated-credential create --id <app-id> --parameters '{
     "name": "github-actions-main",
     "issuer": "https://token.actions.githubusercontent.com",
     "subject": "repo:<org>/<repo>:ref:refs/heads/main",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

3. **Re-run Failed Workflow**

**Recovery Time**: 5 minutes

## Rollback Validation Checklist

After any rollback, verify:

- [ ] Pods are running and healthy: `kubectl get pods -n tail-spin`
- [ ] Health checks passing: `kubectl describe pod <pod-name> -n tail-spin`
- [ ] External IP accessible: `curl http://<external-ip>`
- [ ] Application functionality working (manual test)
- [ ] No errors in pod logs: `kubectl logs -n tail-spin -l app=tailspin-server`
- [ ] Resource usage normal: `kubectl top pods -n tail-spin`
- [ ] Terraform state consistent: `terraform plan` (no changes)
- [ ] Monitoring dashboards show normal metrics
- [ ] Alert rules not firing

## Post-Rollback Actions

1. **Document Incident**:
   - Create GitHub issue with incident report
   - Include timeline, impact, and root cause
   - Tag as `incident`, `rollback`

2. **Communicate Status**:
   - Notify stakeholders of resolution
   - Update status page (if applicable)

3. **Root Cause Analysis**:
   - Identify what went wrong
   - Determine why it wasn't caught earlier
   - Plan preventive measures

4. **Update Procedures**:
   - Improve testing for similar scenarios
   - Add monitoring/alerts if gaps identified
   - Update runbooks with lessons learned

## Prevention Best Practices

- **Test in Non-Prod**: Always test changes in dev/staging first
- **Gradual Rollout**: Use canary or blue-green deployments
- **Monitoring**: Set up alerts for critical metrics
- **Regular Backups**: Maintain backup schedule for stateful data
- **Runbook Maintenance**: Keep rollback procedures up to date
- **Practice Drills**: Regularly test rollback procedures

## Contact and Escalation

- **DevOps Team**: @devops-team (GitHub mention)
- **On-Call**: Check PagerDuty rotation
- **Azure Support**: Open ticket via Azure Portal for infrastructure issues
- **Emergency**: Follow company incident response procedures

## Useful Commands Summary

```bash
# Kubernetes Rollback
kubectl rollout undo deployment/<name> -n tail-spin
kubectl rollout status deployment/<name> -n tail-spin
kubectl rollout history deployment/<name> -n tail-spin

# Image Management
kubectl set image deployment/<name> container=<image>:<tag> -n tail-spin
kubectl describe pod <pod> -n tail-spin | grep Image

# Terraform Rollback
cd infra/ && terraform plan
terraform apply
git revert <commit>

# Verification
kubectl get all -n tail-spin
kubectl logs -n tail-spin -l app=<name>
curl http://<external-ip>
```
