# Root Terraform Configuration
# Orchestrates all infrastructure modules for Tailspin AKS deployment

# Resource Group for all Tailspin infrastructure
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags

  # SAFETY: Defense-in-depth against accidental `terraform destroy`.
  # The provider-level `prevent_deletion_if_contains_resources = true` guard
  # fires at the Azure API layer; this lifecycle block stops the plan itself
  # from generating a destroy action, providing an earlier catch.
  lifecycle {
    prevent_destroy = true
  }
}

# Networking Module - Virtual Network, Subnets, and NSG
module "networking" {
  source = "./modules/networking"

  resource_group_name       = azurerm_resource_group.main.name
  location                  = azurerm_resource_group.main.location
  vnet_name                 = "vnet-${var.project_name}-${var.environment}"
  vnet_address_space        = var.vnet_address_space
  aks_subnet_name           = "snet-${var.project_name}-aks"
  aks_subnet_address_prefix = var.aks_subnet_address_prefix

  tags = local.common_tags
}

# Monitoring Module - Log Analytics and Application Insights
module "monitoring" {
  source = "./modules/monitoring"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_name      = "log-${var.project_name}-${var.environment}"
  appinsights_name    = "appi-${var.project_name}-${var.environment}"
  retention_in_days   = var.log_retention_days

  tags = local.common_tags
}

# Azure Container Registry Module
module "acr" {
  source = "./modules/acr"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  acr_name            = "acr${var.project_name}${var.environment}"
  sku                 = "Premium"
  admin_enabled       = false

  # SECURITY: Disable public registry access; images are pulled over the private
  # AKS subnet path. A private endpoint for ACR must be configured separately.
  # See docs/azure-setup-guide.md § "ACR Private Endpoint".
  public_network_access_enabled = false

  tags = local.common_tags
}

# AKS Cluster Module
module "aks" {
  source = "./modules/aks"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  cluster_name        = "aks-${var.project_name}-${var.environment}"
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  # Node pool configuration
  node_pool_vm_size   = var.node_pool_vm_size
  node_pool_min_count = var.node_pool_min_count
  node_pool_max_count = var.node_pool_max_count

  # API server access restriction
  api_server_authorized_ip_ranges = var.api_server_authorized_ip_ranges

  # Network integration (implicit dependency on module.networking)
  subnet_id = module.networking.aks_subnet_id

  # Monitoring integration (implicit dependency on module.monitoring)
  log_analytics_workspace_id = module.monitoring.workspace_id

  tags = local.common_tags
}

# RBAC Module - AKS to ACR managed-identity role assignment
module "rbac" {
  source = "./modules/rbac"

  aks_kubelet_identity_object_id = module.aks.kubelet_identity_object_id
  acr_id                         = module.acr.acr_id

  depends_on = [module.aks, module.acr]
}

# Common tags applied to every resource in this deployment.
# Add environment-specific overrides at the call site if needed.
locals {
  common_tags = {
    Application      = "TailspinToystore"
    CostCenter       = var.cost_center
    Environment      = var.environment
    ManagedBy        = "Terraform"
    Owner            = var.owner
    Project          = "Tailspin"
    Repository       = "tailspin-toystore"
    TerraformWorkspace = terraform.workspace
  }
}
