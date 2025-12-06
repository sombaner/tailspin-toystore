# Azure Setup Guide for AKS Deployment Automation

This guide covers the one-time Azure and GitHub configuration required before running the automated deployment pipelines.

## Prerequisites

- Azure subscription with sufficient quota for AKS and ACR in Central India region
- Azure CLI installed and configured (`az --version`)
- GitHub repository with Actions enabled
- Owner or Contributor role in Azure subscription
- GitHub repository admin access

## Step 1: Azure AD Application Setup for GitHub OIDC

GitHub Actions will authenticate to Azure using OpenID Connect (OIDC) without storing credentials as secrets.

### 1.1 Create Azure AD Application

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "<your-subscription-id>"

# Create Azure AD application
APP_NAME="github-actions-tailspin"
az ad app create --display-name "$APP_NAME"

# Get the Application (client) ID
APP_ID=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)
echo "Application ID: $APP_ID"

# Create service principal for the application
az ad sp create --id "$APP_ID"

# Get the Object ID of the service principal
SP_OBJECT_ID=$(az ad sp list --display-name "$APP_NAME" --query "[0].id" -o tsv)
echo "Service Principal Object ID: $SP_OBJECT_ID"
```

### 1.2 Configure Federated Identity Credentials

**Important**: The subject claim format depends on whether your workflows use GitHub Environments.

#### Option A: Without GitHub Environments (Recommended for Simple Setup)

If your workflows don't specify `environment: production`, use these federated credentials:

```bash
# Get your GitHub repository details
GITHUB_ORG="<your-github-org>"  # e.g., "sombaner"
GITHUB_REPO="<your-repo-name>"  # e.g., "tailspin-toystore"

# Create federated credential for main branch
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG"'/'"$GITHUB_REPO"':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Create federated credential for pull requests (optional but recommended)
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-pr",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG"'/'"$GITHUB_REPO"':pull_request",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

#### Option B: With GitHub Environments (For Approval Gates)

If your workflows use `environment: production` for approval gates, you need additional federated credentials:

```bash
# Create federated credential for production environment
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-production-env",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG"'/'"$GITHUB_REPO"':environment:production",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Create federated credential for staging environment (if used)
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-staging-env",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG"'/'"$GITHUB_REPO"':environment:staging",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Note**: When using GitHub Environments in workflows, the subject claim changes from `ref:refs/heads/main` to `environment:<env-name>`. If you get an error like `AADSTS700213: No matching federated identity record found for presented assertion subject`, you need to add the appropriate environment-based federated credential shown above.

### 1.3 Assign Azure RBAC Permissions

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Subscription ID: $SUBSCRIPTION_ID"

# Get your tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "Tenant ID: $TENANT_ID"

# Assign Contributor role at subscription level
# (You can scope this to a specific resource group after creation)
az role assignment create \
  --assignee "$APP_ID" \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"

# If you want to scope to resource group (after creating it):
# az role assignment create \
#   --assignee "$APP_ID" \
#   --role "Contributor" \
#   --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-sb-aks-01"
```

## Step 2: Azure Storage Account for Terraform State

Terraform state must be stored remotely with locking enabled for team collaboration and CI/CD.

### 2.1 Create Resource Group for Terraform State

```bash
# Create resource group for Terraform state (separate from application resources)
az group create \
  --name "rg-terraform-state" \
  --location "centralindia"
```

### 2.2 Create Storage Account

```bash
# Generate unique storage account name (must be globally unique, 3-24 chars, lowercase alphanumeric)
STORAGE_ACCOUNT_NAME="sttfstateprod$(openssl rand -hex 3)"
echo "Storage Account Name: $STORAGE_ACCOUNT_NAME"

# Create storage account with secure defaults
az storage account create \
  --name "$STORAGE_ACCOUNT_NAME" \
  --resource-group "rg-terraform-state" \
  --location "centralindia" \
  --sku "Standard_LRS" \
  --kind "StorageV2" \
  --min-tls-version "TLS1_2" \
  --allow-blob-public-access false \
  --https-only true

# Enable versioning for state file protection
az storage account blob-service-properties update \
  --account-name "$STORAGE_ACCOUNT_NAME" \
  --enable-versioning true
```

### 2.3 Create Blob Container for State Files

```bash
# Create container for Terraform state
az storage container create \
  --name "tfstate" \
  --account-name "$STORAGE_ACCOUNT_NAME" \
  --auth-mode login
```

### 2.4 Grant Service Principal Access to Storage

**Important**: When using OIDC authentication with Terraform Azure backend, the service principal needs permissions to both read storage account properties and access blob data.

```bash
# Option 1: Assign Storage Account Contributor role (Recommended - includes all necessary permissions)
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Account Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Option 2: Assign both Storage Blob Data Contributor and Reader roles (More restrictive)
# This provides blob data access and read access to storage account properties
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

az role assignment create \
  --assignee "$APP_ID" \
  --role "Reader" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"
```

**Note**: The **Storage Account Contributor** role includes `Microsoft.Storage/storageAccounts/listKeys/action` which Terraform may attempt to use during backend initialization. If you prefer least-privilege access, use Option 2 which provides read-only access to storage account metadata plus full blob data access.

### 2.5 Update Terraform Backend Configuration

Update `infra/backend.tf` with your storage account name:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "<your-storage-account-name>"  # Replace with $STORAGE_ACCOUNT_NAME
    container_name       = "tfstate"
    key                  = "tailspin-aks.tfstate"
    use_oidc             = true
  }
}
```

## Step 3: Configure GitHub Secrets

GitHub Actions workflows require these secrets for Azure authentication.

### 3.1 Add Repository Secrets

Go to your GitHub repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

1. **AZURE_CLIENT_ID**
   - Value: The Application (client) ID from Step 1.1 (`$APP_ID`)
   - Example: `12345678-1234-1234-1234-123456789012`

2. **AZURE_TENANT_ID**
   - Value: The Tenant ID from Step 1.3 (`$TENANT_ID`)
   - Example: `87654321-4321-4321-4321-210987654321`

3. **AZURE_SUBSCRIPTION_ID**
   - Value: The Subscription ID from Step 1.3 (`$SUBSCRIPTION_ID`)
   - Example: `abcdef12-3456-7890-abcd-ef1234567890`

### 3.2 Verify Secret Configuration

Create a test workflow or check the existing workflows use this pattern:

```yaml
- name: Azure Login via OIDC
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Step 4: Verify Configuration

### 4.1 Test Azure Authentication Locally (Optional)

```bash
# Verify service principal can authenticate
az login --service-principal \
  --username "$APP_ID" \
  --tenant "$TENANT_ID" \
  # Note: OIDC auth requires GitHub Actions context, so local testing uses certificate or password

# List resources to verify permissions
az resource list --resource-group "rg-terraform-state"
```

### 4.2 Test Terraform Backend Access

```bash
cd infra/

# Initialize Terraform (will connect to Azure Storage backend)
terraform init

# Expected output: "Successfully configured the backend 'azurerm'!"
```

### 4.3 Validate Backend Configuration (Recommended)

Use the provided validation script to verify all permissions are correctly configured:

```bash
# Run from repository root
./scripts/validate-terraform-backend.sh "$APP_ID" "$STORAGE_ACCOUNT_NAME"
```

This script will:
- ✅ Verify Azure CLI authentication
- ✅ Check if storage account exists
- ✅ Validate RBAC role assignments on the storage account
- ✅ Confirm the service principal has necessary permissions
- ✅ Ensure the tfstate container exists
- ✅ Provide specific remediation steps if issues are found

**Expected Output**:
```
==========================================
Terraform Backend Validation
==========================================

✓ Azure CLI is installed
✓ Logged in to Azure
  Subscription ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
✓ Storage account 'sttfstateprod' exists
✓ Found role assignments:
  - Storage Account Contributor
✓ Service principal has Storage Account Contributor role (includes all necessary permissions)
✓ Container 'tfstate' exists

==========================================
✓ Validation completed successfully!
==========================================
```

## Step 5: Create Application Resource Group (Optional)

You can pre-create the application resource group, or let Terraform create it:

```bash
# Option 1: Pre-create resource group
az group create \
  --name "rg-sb-aks-01" \
  --location "centralindia"

# Option 2: Let Terraform create it (recommended)
# The resource group will be created when you run terraform apply
```

## Summary of Created Resources

After completing this setup, you will have:

- ✅ Azure AD Application registered for GitHub OIDC authentication
- ✅ Service Principal with Contributor role in subscription
- ✅ Federated identity credentials for GitHub Actions
- ✅ Storage account for Terraform remote state with versioning
- ✅ Blob container for state files with proper access controls
- ✅ GitHub repository secrets configured (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID)

## Next Steps

1. Update `infra/backend.tf` with your storage account name
2. Commit the infrastructure code to your repository
3. Trigger the infrastructure deployment workflow: `.github/workflows/infra-deploy.yml`
4. Monitor the workflow execution in GitHub Actions

## Troubleshooting

### Issue: "Error: Failed to get existing workspaces: Error retrieving keys for Storage Account"

**Full Error**:
```
Error: Failed to get existing workspaces: Error retrieving keys for Storage Account "sttfstateprod": 
storage.AccountsClient#ListKeys: Failure responding to request: StatusCode=403 -- Original Error: 
autorest/azure: Service returned an error. Status=403 Code="AuthorizationFailed" 
Message="The client '***' with object id '...' does not have authorization to perform action 
'Microsoft.Storage/storageAccounts/listKeys/action' over scope '/subscriptions/.../resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/sttfstateprod' 
or the scope is invalid."
```

**Root Cause**: The service principal lacks sufficient permissions on the Terraform state storage account. When using OIDC authentication, Terraform needs both blob data access and storage account read permissions.

**Solution**: Grant the service principal appropriate RBAC roles on the storage account:

```bash
# Get your service principal App ID and storage account details
APP_ID="<your-app-id>"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
STORAGE_ACCOUNT_NAME="<your-storage-account-name>"

# Option 1: Assign Storage Account Contributor role (Recommended)
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Account Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Option 2: Assign both Storage Blob Data Contributor and Reader roles
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

az role assignment create \
  --assignee "$APP_ID" \
  --role "Reader" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Verify the role assignments
az role assignment list \
  --assignee "$APP_ID" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME" \
  --output table
```

**After applying the fix**, wait 5-10 minutes for Azure RBAC permissions to propagate, then re-run the workflow.

### Issue: "Error building ARM Config: obtain subscription() from Azure CLI: parsing json result from the Azure CLI"

**Solution**: Ensure you're logged in with `az login` and the correct subscription is set with `az account set`.

### Issue: "Error: building account: could not acquire access token to parse claims"

**Solution**: Verify that federated credentials are correctly configured and GitHub Actions has the correct secrets.

### Issue: "The subscription is not registered to use namespace 'Microsoft.ContainerService'"

**Solution**: Register the required resource providers:

```bash
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.OperationalInsights
```

### Issue: "Insufficient quota for AKS nodes"

**Solution**: Request quota increase in Azure Portal → Subscriptions → Usage + quotas, or use smaller VM sizes.

## Security Best Practices

- ✅ Use OIDC authentication (no long-lived credentials)
- ✅ Scope service principal permissions to specific resource groups when possible
- ✅ Enable storage account versioning for state file recovery
- ✅ Use private endpoints for storage account in production
- ✅ Rotate service principal credentials regularly (if using certificate/password auth)
- ✅ Review federated credential subjects to limit authentication scope
- ✅ Enable Azure Policy for compliance checks on created resources

## References

- [GitHub Actions OIDC with Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- [Terraform Azure Backend](https://developer.hashicorp.com/terraform/language/settings/backends/azurerm)
- [Azure Service Principal OIDC](https://learn.microsoft.com/en-us/azure/active-directory/develop/workload-identity-federation)
