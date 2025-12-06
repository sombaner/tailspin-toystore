# Terraform Backend Configuration for Azure Storage
# This configuration stores Terraform state remotely in Azure Storage
# with state locking enabled via blob lease mechanism
#
# NOTE: The storage_account_name must be updated with your actual storage account name
# after running the Azure setup guide (docs/azure-setup-guide.md)
# Backend configuration does not support variable interpolation

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstateprod"  # Update this with your storage account name
    container_name       = "tfstate"
    key                  = "tailspin-aks.tfstate"
    use_oidc             = true
  }
}
