# Terraform Backend Authentication Fix

## Problem

When running the Infrastructure Deployment GitHub Action, you encounter this error:

```
Error: Failed to get existing workspaces: Error retrieving keys for Storage Account "sttfstateprod": 
storage.AccountsClient#ListKeys: Failure responding to request: StatusCode=403 -- Original Error: 
autorest/azure: Service returned an error. Status=403 Code="AuthorizationFailed" 
Message="The client '***' with object id '...' does not have authorization to perform action 
'Microsoft.Storage/storageAccounts/listKeys/action' over scope 
'/subscriptions/.../resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/sttfstateprod' 
or the scope is invalid. If access was recently granted, please refresh your credentials."
```

## Root Cause

The GitHub Actions service principal lacks sufficient RBAC permissions on the Terraform state storage account. When using OIDC authentication with Azure Storage backend, Terraform requires permissions to:

1. **Read storage account properties** (control plane operations)
2. **Access blob data** (data plane operations)

The original setup guide only granted **Storage Blob Data Contributor** role, which provides blob data access but not storage account read permissions.

## Quick Fix

Choose **ONE** of the following options:

### Option 1: Storage Account Contributor Role (Recommended)

This role includes all necessary permissions for Terraform backend access.

```bash
# Get your service principal App ID from GitHub Secrets (AZURE_CLIENT_ID)
APP_ID="<your-app-id>"

# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Get your storage account name (from infra/backend.tf)
STORAGE_ACCOUNT_NAME="<your-storage-account-name>"

# Assign Storage Account Contributor role
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Account Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Verify the assignment
az role assignment list \
  --assignee "$APP_ID" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME" \
  --output table
```

### Option 2: Storage Blob Data Contributor + Reader Roles

This provides more granular permissions with least-privilege access.

```bash
# Assign Storage Blob Data Contributor role (for blob operations)
az role assignment create \
  --assignee "$APP_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Assign Reader role (for storage account metadata)
az role assignment create \
  --assignee "$APP_ID" \
  --role "Reader" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Verify the assignments
az role assignment list \
  --assignee "$APP_ID" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME" \
  --output table
```

## Validation

### Automated Validation

Use the provided validation script to verify your configuration:

```bash
./scripts/validate-terraform-backend.sh "$APP_ID" "$STORAGE_ACCOUNT_NAME"
```

The script will check all necessary permissions and provide specific remediation steps if issues are found.

### Manual Verification

1. **Wait for permissions to propagate** (5-10 minutes after role assignment)

2. **Test locally** (optional):
   ```bash
   cd infra/
   terraform init
   ```

3. **Re-run the GitHub Actions workflow**:
   - Go to Actions tab in your GitHub repository
   - Select "Infrastructure Deployment" workflow
   - Click "Run workflow"
   - Select action: "plan"
   - Click "Run workflow"

## Expected Results

After applying the fix, you should see:

```
Initializing the backend...

Successfully configured the backend "azurerm"!

Terraform has been successfully initialized!
```

## Prevention

To prevent this issue in the future:

1. **Always use the validation script** after initial Azure setup:
   ```bash
   ./scripts/validate-terraform-backend.sh "$APP_ID" "$STORAGE_ACCOUNT_NAME"
   ```

2. **Follow the updated Azure setup guide**: [docs/azure-setup-guide.md](./azure-setup-guide.md)

3. **Document your setup**: Keep track of:
   - Application ID (Client ID)
   - Storage account name
   - Resource group names
   - Role assignments

## Permissions Explained

### Why Storage Account Contributor?

The **Storage Account Contributor** role includes:
- `Microsoft.Storage/storageAccounts/read` - Read storage account properties
- `Microsoft.Storage/storageAccounts/listKeys/action` - List storage account keys
- All blob data operations via data plane

This is the recommended role because it provides all necessary permissions in a single assignment.

### Why Storage Blob Data Contributor + Reader?

This combination provides least-privilege access:
- **Storage Blob Data Contributor**: Full blob data access (read, write, delete)
- **Reader**: Read storage account metadata (but cannot list keys or modify settings)

While more restrictive, this combination still allows Terraform to function correctly because:
- Terraform uses OIDC authentication (doesn't need key-based access)
- The Reader role provides enough metadata access for backend initialization
- Blob operations use data plane RBAC (Storage Blob Data Contributor)

## Additional Resources

- [Azure Setup Guide](./azure-setup-guide.md) - Complete setup instructions
- [GitHub Actions OIDC with Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- [Terraform Azure Backend](https://developer.hashicorp.com/terraform/language/settings/backends/azurerm)
- [Azure RBAC Roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)

## Troubleshooting

### Issue: Permissions still not working after role assignment

**Solution**: Azure RBAC permissions can take 5-10 minutes to propagate. Wait and then retry the workflow.

### Issue: "Cannot find service principal with App ID"

**Solution**: Verify you're using the correct App ID from GitHub Secrets (AZURE_CLIENT_ID), not the Object ID.

```bash
# Get App ID from Azure AD
az ad sp list --display-name "github-actions-tailspin" --query "[0].appId" -o tsv
```

### Issue: "Storage account not found"

**Solution**: Verify the storage account exists and you're using the correct name:

```bash
az storage account list --resource-group "rg-terraform-state" --query "[].name" -o tsv
```

### Issue: Multiple role assignments exist

**Solution**: If you assigned multiple roles during troubleshooting, you can remove unnecessary ones:

```bash
# List all role assignments
az role assignment list \
  --assignee "$APP_ID" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME" \
  --output table

# Remove a specific role assignment (if needed)
az role assignment delete \
  --assignee "$APP_ID" \
  --role "<role-name>" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-terraform-state/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"
```

## Support

If you continue to experience issues:

1. Run the validation script and save the output
2. Check GitHub Actions logs for the specific error
3. Verify all GitHub Secrets are correctly configured
4. Review the Azure setup guide for any missed steps
5. Open an issue in the repository with:
   - Validation script output
   - GitHub Actions error logs (redact sensitive information)
   - Steps already attempted
