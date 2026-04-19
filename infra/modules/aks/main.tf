# AKS Module - Azure Kubernetes Service Cluster

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  sku_tier = "Standard"

  # Default node pool configuration
  default_node_pool {
    name                = "system"
    vm_size             = var.node_pool_vm_size
    vnet_subnet_id      = var.subnet_id
    enable_auto_scaling = true
    min_count           = var.node_pool_min_count
    max_count           = var.node_pool_max_count
    # 128 GB minimum for production workloads; 30 GB causes disk-pressure evictions.
    os_disk_size_gb = var.os_disk_size_gb
    type            = "VirtualMachineScaleSets"

    # Prevent Terraform from fighting the cluster autoscaler over node_count.
    # Without this, every plan shows a spurious diff and risks accidental scale-downs.
    lifecycle {
      ignore_changes = [node_count]
    }
  }

  # Managed identity for AKS cluster
  identity {
    type = "SystemAssigned"
  }

  # Network profile
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = var.service_cidr
    dns_service_ip    = var.dns_service_ip
  }

  # Restrict API-server access to known CIDR ranges.
  # SECURITY: An empty list means ALL internet IPs can reach the Kubernetes
  # control plane. This MUST NOT be empty in production.
  # Set var.api_server_authorized_ip_ranges to your CI/CD agent egress IPs
  # and operator/bastion ranges before deploying.
  # Violation of this setting breaches CIS AKS Benchmark 6.6.1.
  api_server_access_profile {
    authorized_ip_ranges = var.api_server_authorized_ip_ranges
  }

  # OMS agent for Log Analytics monitoring integration
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  # Lifecycle protection: prevent accidental cluster destruction.
  lifecycle {
    prevent_destroy = true
  }

  tags = var.tags
}
