# Terraform Providers Configuration
# Configures Azure provider with OIDC authentication for GitHub Actions
#
# Required environment variables (set in CI/CD pipeline secrets):
#   ARM_CLIENT_ID       - Client ID of the GitHub Actions federated identity
#   ARM_TENANT_ID       - Azure AD tenant ID
#   ARM_SUBSCRIPTION_ID - Target Azure subscription ID
#
# For local development, authenticate via: az login && az account set --subscription <id>

terraform {
  # Upper-bound < 2.0.0 prevents accidental adoption of a future Terraform 2.x
  # major release that may introduce breaking language or provider-framework changes.
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
}

# Azure Resource Manager provider
# Uses OIDC authentication when use_oidc is enabled (GitHub Actions)
provider "azurerm" {
  features {
    resource_group {
      # SAFETY: Prevents accidental destruction of non-empty resource groups.
      # If Terraform tries to delete a resource group that still contains
      # resources, the apply will fail with a clear error instead of silently
      # deleting everything.
      prevent_deletion_if_contains_resources = true
    }
    key_vault {
      # SAFETY: Keep soft-deleted Key Vaults recoverable for 90 days.
      # Purging immediately on destroy bypasses Azure's recoverability window
      # and risks permanent, unrecoverable secret loss.
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
  }

  use_oidc = true
}
