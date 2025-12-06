# Root Terraform Configuration
# Orchestrates all infrastructure modules for Tailspin AKS deployment

# Resource Group for all Tailspin infrastructure
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

# Networking Module - Virtual Network and Subnets
module "networking" {
  source = "./modules/networking"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  vnet_name           = "vnet-${var.project_name}-${var.environment}"
  vnet_address_space  = var.vnet_address_space
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

  tags = local.common_tags
}

# AKS Cluster Module
module "aks" {
  source = "./modules/aks"

  resource_group_name         = azurerm_resource_group.main.name
  location                    = azurerm_resource_group.main.location
  cluster_name                = "aks-${var.project_name}-${var.environment}"
  dns_prefix                  = "${var.project_name}-${var.environment}"
  kubernetes_version          = var.kubernetes_version
  
  # Node pool configuration
  node_pool_vm_size          = var.node_pool_vm_size
  node_pool_min_count        = var.node_pool_min_count
  node_pool_max_count        = var.node_pool_max_count
  
  # Network integration
  subnet_id                   = module.networking.aks_subnet_id
  
  # Monitoring integration
  log_analytics_workspace_id  = module.monitoring.workspace_id

  tags = local.common_tags

  depends_on = [module.networking, module.monitoring]
}

# RBAC Module - AKS to ACR authentication
module "rbac" {
  source = "./modules/rbac"

  aks_kubelet_identity_object_id = module.aks.kubelet_identity_object_id
  acr_id                         = module.acr.acr_id
  resource_group_name            = azurerm_resource_group.main.name

  depends_on = [module.aks, module.acr]
}

# Common tags for all resources
locals {
  common_tags = {
    Environment = var.environment
    Project     = "Tailspin"
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}
