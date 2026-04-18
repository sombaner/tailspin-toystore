# AKS Module Variables

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix for AKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster. MUST be an exact patch version (e.g. '1.28.5'). A partial version like '1.28' causes continuous state drift: Azure resolves it to a patch release, so every subsequent plan shows a diff wanting to revert."
  type        = string
  default     = "1.28.5"

  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+$", var.kubernetes_version))
    error_message = "kubernetes_version must be a full semantic version string (e.g. '1.28.5'), not a partial version like '1.28'."
  }
}

variable "node_pool_vm_size" {
  description = "VM size for node pool"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "node_pool_min_count" {
  description = "Minimum number of nodes in node pool. Must be >= 2 for production HA: a single-node system pool cannot tolerate a node upgrade or eviction without workload disruption."
  type        = number
  default     = 2

  validation {
    condition     = var.node_pool_min_count >= 2
    error_message = "node_pool_min_count must be at least 2 for production high availability. A single-node pool cannot tolerate node-level maintenance without downtime."
  }
}

variable "node_pool_max_count" {
  description = "Maximum number of nodes in node pool"
  type        = number
  default     = 3

  validation {
    condition     = var.node_pool_max_count >= 1
    error_message = "node_pool_max_count must be at least 1."
  }
}

variable "os_disk_size_gb" {
  description = "OS disk size in GB for AKS node pool. Minimum 128 GB recommended for production."
  type        = number
  default     = 128

  validation {
    condition     = var.os_disk_size_gb >= 30
    error_message = "os_disk_size_gb must be at least 30 GB."
  }
}

variable "service_cidr" {
  description = "CIDR range for Kubernetes services. Must not overlap with the VNet or AKS subnet address space."
  type        = string
  default     = "10.1.0.0/16"
}

variable "dns_service_ip" {
  description = "IP address for Kubernetes DNS service. Must be within service_cidr range."
  type        = string
  default     = "10.1.0.10"
}

variable "api_server_authorized_ip_ranges" {
  description = "List of CIDR ranges permitted to reach the AKS API server. An empty list allows all IPs (not recommended for production). Set to your CI/CD agent egress IPs and operator ranges."
  type        = list(string)
  default     = []
}

variable "subnet_id" {
  description = "Subnet ID for AKS cluster"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for monitoring"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
