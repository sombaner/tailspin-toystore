# AKS Module - Azure Kubernetes Service Automatic Cluster

# AKS Cluster with Automatic mode
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  # AKS Automatic mode configuration
  sku_tier = "Standard"

  # Default node pool configuration
  default_node_pool {
    name                = "system"
    vm_size             = var.node_pool_vm_size
    vnet_subnet_id      = var.subnet_id
    enable_auto_scaling = true
    min_count           = var.node_pool_min_count
    max_count           = var.node_pool_max_count
    os_disk_size_gb     = 30
    type                = "VirtualMachineScaleSets"
  }

  # Managed identity for AKS cluster
  identity {
    type = "SystemAssigned"
  }

  # Network profile for public cluster
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }

  # OMS agent for monitoring integration
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  # Azure Monitor for containers
  azure_monitor {
    enabled = true
  }

  tags = var.tags
}
