# Azure Container Registry Module

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  admin_enabled       = var.admin_enabled

  # SECURITY: Disable public internet access to the registry.
  # Requires a private endpoint or VNet service endpoint so that AKS kubelet
  # can still pull images over the private network path.
  # If no private endpoint exists yet, set public_network_access_enabled = true
  # temporarily and create the private endpoint before switching back to false.
  public_network_access_enabled = var.public_network_access_enabled

  # DATA RETENTION: Automatically delete untagged manifests after retention_days.
  # Only effective on Premium SKU. Prevents unbounded storage growth and makes
  # the registry easier to audit for stale / untested images.
  dynamic "retention_policy" {
    for_each = var.sku == "Premium" ? [1] : []
    content {
      days    = var.retention_days
      enabled = var.retention_days > 0
    }
  }

  # Enable geo-replication for Premium SKU
  dynamic "georeplications" {
    for_each = var.sku == "Premium" ? var.georeplications : []
    content {
      location                = georeplications.value.location
      zone_redundancy_enabled = georeplications.value.zone_redundancy_enabled
    }
  }

  tags = var.tags

  # SAFETY: ACR destruction permanently deletes all container images.
  # There is no soft-delete or recovery mechanism for ACR resources.
  # Require explicit lifecycle override to destroy.
  lifecycle {
    prevent_destroy = true
  }
}
