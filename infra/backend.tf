# Terraform Backend Configuration for Azure Storage
# This configuration stores Terraform state remotely in Azure Storage
# with state locking enabled via blob lease mechanism

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstate${var.environment}"
    container_name       = "tfstate"
    key                  = "tailspin-aks.tfstate"
    use_oidc             = true
  }
}
