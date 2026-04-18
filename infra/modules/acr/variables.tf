# ACR Module Variables

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "acr_name" {
  description = "Name of the Azure Container Registry (must be globally unique)"
  type        = string
}

variable "sku" {
  description = "SKU for Azure Container Registry (Basic, Standard, Premium)"
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "admin_enabled" {
  description = "Enable admin user for ACR (not recommended for production)"
  type        = bool
  default     = false
}

variable "public_network_access_enabled" {
  description = <<-EOT
    Whether public network access to the ACR is permitted.
    Set to false (recommended for production) and configure a private endpoint
    or a VNet service endpoint so that AKS nodes can still pull images.
    Requires Premium SKU; ignored for Basic/Standard where network rules are unavailable.
    WARNING: setting to false without a private endpoint will break AKS image pulls.
  EOT
  type        = bool
  default     = false
}

variable "retention_days" {
  description = "Number of days to retain untagged manifests. Only effective on Premium SKU. Range: 1–365. Set to 0 to disable."
  type        = number
  default     = 30

  validation {
    condition     = var.retention_days >= 0 && var.retention_days <= 365
    error_message = "retention_days must be between 0 and 365."
  }
}

variable "georeplications" {
  description = "List of geo-replication locations for Premium SKU"
  type = list(object({
    location                = string
    zone_redundancy_enabled = bool
  }))
  default = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
