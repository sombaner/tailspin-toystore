#!/bin/bash

# Terraform Backend Validation Script
# This script validates that the service principal has the necessary permissions
# to access the Terraform state storage account using OIDC authentication.
#
# Usage:
#   ./scripts/validate-terraform-backend.sh <APP_ID> <STORAGE_ACCOUNT_NAME>
#
# Example:
#   ./scripts/validate-terraform-backend.sh "12345678-1234-1234-1234-123456789012" "sttfstateprod"

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "$1"
}

# Check arguments
if [ $# -lt 2 ]; then
    print_error "Usage: $0 <APP_ID> <STORAGE_ACCOUNT_NAME>"
    echo ""
    echo "Example:"
    echo "  $0 \"12345678-1234-1234-1234-123456789012\" \"sttfstateprod\""
    exit 1
fi

APP_ID="$1"
STORAGE_ACCOUNT_NAME="$2"
RESOURCE_GROUP="rg-terraform-state"

print_info "=========================================="
print_info "Terraform Backend Validation"
print_info "=========================================="
echo ""

# Check if Azure CLI is installed
print_info "Checking Azure CLI installation..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi
print_success "Azure CLI is installed"
echo ""

# Check if logged in to Azure
print_info "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Logged in to Azure"
print_info "  Subscription ID: $SUBSCRIPTION_ID"
echo ""

# Verify storage account exists
print_info "Checking if storage account exists..."
if ! az storage account show --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_error "Storage account '$STORAGE_ACCOUNT_NAME' not found in resource group '$RESOURCE_GROUP'"
    print_warning "Please create the storage account first using the Azure Setup Guide"
    exit 1
fi
print_success "Storage account '$STORAGE_ACCOUNT_NAME' exists"
echo ""

# Check role assignments
print_info "Checking RBAC role assignments for service principal..."
STORAGE_ACCOUNT_SCOPE="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"

# Get all role assignments for the service principal on the storage account
ROLE_ASSIGNMENTS=$(az role assignment list \
    --assignee "$APP_ID" \
    --scope "$STORAGE_ACCOUNT_SCOPE" \
    --query "[].roleDefinitionName" -o tsv)

if [ -z "$ROLE_ASSIGNMENTS" ]; then
    print_error "No role assignments found for service principal on storage account"
    echo ""
    print_warning "To fix this, run ONE of the following commands:"
    echo ""
    echo "Option 1 (Recommended): Assign Storage Account Contributor role"
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Storage Account Contributor\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    echo ""
    echo "Option 2: Assign both Storage Blob Data Contributor and Reader roles"
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Storage Blob Data Contributor\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    echo ""
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Reader\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    exit 1
fi

print_success "Found role assignments:"
echo "$ROLE_ASSIGNMENTS" | while read -r role; do
    print_info "  - $role"
done
echo ""

# Check for required permissions
HAS_STORAGE_ACCOUNT_CONTRIBUTOR=false
HAS_STORAGE_BLOB_DATA_CONTRIBUTOR=false
HAS_READER=false
HAS_CONTRIBUTOR=false

while IFS= read -r role; do
    case "$role" in
        "Storage Account Contributor")
            HAS_STORAGE_ACCOUNT_CONTRIBUTOR=true
            ;;
        "Storage Blob Data Contributor")
            HAS_STORAGE_BLOB_DATA_CONTRIBUTOR=true
            ;;
        "Reader")
            HAS_READER=true
            ;;
        "Contributor")
            HAS_CONTRIBUTOR=true
            ;;
    esac
done <<< "$ROLE_ASSIGNMENTS"

print_info "Validating required permissions..."

# Check if service principal has sufficient permissions
PERMISSIONS_OK=false

if [ "$HAS_STORAGE_ACCOUNT_CONTRIBUTOR" = true ] || [ "$HAS_CONTRIBUTOR" = true ]; then
    print_success "Service principal has Storage Account Contributor role (includes all necessary permissions)"
    PERMISSIONS_OK=true
elif [ "$HAS_STORAGE_BLOB_DATA_CONTRIBUTOR" = true ] && [ "$HAS_READER" = true ]; then
    print_success "Service principal has Storage Blob Data Contributor and Reader roles"
    PERMISSIONS_OK=true
elif [ "$HAS_STORAGE_BLOB_DATA_CONTRIBUTOR" = true ]; then
    print_warning "Service principal has Storage Blob Data Contributor role but missing Reader role"
    print_warning "Terraform may fail to initialize backend. Add Reader role with:"
    echo ""
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Reader\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    echo ""
    exit 1
else
    print_error "Service principal does not have sufficient permissions"
    echo ""
    print_warning "To fix this, run ONE of the following commands:"
    echo ""
    echo "Option 1 (Recommended): Assign Storage Account Contributor role"
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Storage Account Contributor\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    echo ""
    echo "Option 2: Assign both Storage Blob Data Contributor and Reader roles"
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Storage Blob Data Contributor\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    echo ""
    echo "  az role assignment create \\"
    echo "    --assignee \"$APP_ID\" \\"
    echo "    --role \"Reader\" \\"
    echo "    --scope \"$STORAGE_ACCOUNT_SCOPE\""
    exit 1
fi
echo ""

# Check if blob container exists
print_info "Checking if tfstate container exists..."
if ! az storage container exists \
    --name "tfstate" \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --auth-mode login \
    --query "exists" -o tsv | grep -q "true"; then
    print_warning "Container 'tfstate' does not exist. Creating it..."
    az storage container create \
        --name "tfstate" \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --auth-mode login > /dev/null
    print_success "Container 'tfstate' created"
else
    print_success "Container 'tfstate' exists"
fi
echo ""

# Final summary
print_info "=========================================="
if [ "$PERMISSIONS_OK" = true ]; then
    print_success "Validation completed successfully!"
    print_info "Your service principal has the necessary permissions for Terraform backend access."
    print_info ""
    print_info "Next steps:"
    print_info "  1. Ensure infra/backend.tf has the correct storage_account_name: $STORAGE_ACCOUNT_NAME"
    print_info "  2. Run 'cd infra && terraform init' to initialize Terraform backend"
    print_info "  3. Run the Infrastructure Deployment workflow in GitHub Actions"
else
    print_error "Validation failed - please fix the issues above"
    exit 1
fi
print_info "=========================================="
