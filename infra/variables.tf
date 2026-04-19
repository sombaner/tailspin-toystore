# Terraform Variables for Tailspin AKS Deployment

# Environment and Location
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region for resource deployment"
  type        = string
  default     = "centralindia"

  validation {
    condition     = length(var.location) > 0
    error_message = "location must be a non-empty Azure region string."
  }
}

variable "resource_group_name" {
  description = "Name of the Azure resource group. Must follow org naming convention: rg-<project>-<env>."
  type        = string
  default     = "rg-tailspin-prod"

  validation {
    condition     = can(regex("^rg-", var.resource_group_name))
    error_message = "resource_group_name must start with 'rg-'."
  }
}

# Project Configuration
variable "project_name" {
  description = "Project name used for resource naming (lowercase alphanumeric)"
  type        = string
  default     = "tailspin"

  validation {
    condition     = can(regex("^[a-z0-9]+$", var.project_name))
    error_message = "project_name must be lowercase alphanumeric only."
  }
}

variable "owner" {
  description = "Owner tag value for resources (team or person accountable)"
  type        = string
  default     = "DevOps Team"
}

variable "cost_center" {
  description = "Cost center tag for resource billing attribution"
  type        = string
  default     = "Engineering"
}

# Networking Configuration
variable "vnet_address_space" {
  description = "Address space for the virtual network (list of CIDR blocks)"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "aks_subnet_address_prefix" {
  description = "Address prefix for AKS subnet (must be within vnet_address_space)"
  type        = string
  default     = "10.0.1.0/24"
}

# AKS Configuration
variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster. MUST be pinned to an exact patch version (e.g. '1.28.5'). Omitting the patch component (e.g. '1.28') causes state drift: Azure auto-patches the cluster to '1.28.5', after which every `terraform plan` shows a spurious diff trying to revert to '1.28'."
  type        = string
  default     = "1.28.5"

  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+$", var.kubernetes_version))
    error_message = "kubernetes_version must be a full semantic version string (e.g. '1.28.5'), not a partial version like '1.28'."
  }
}

variable "node_pool_vm_size" {
  description = "VM size for AKS node pool"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "node_pool_min_count" {
  description = "Minimum number of nodes in the node pool. Minimum of 2 required for production high availability (node upgrade buffer, PodDisruptionBudget compliance)."
  type        = number
  default     = 2

  validation {
    condition     = var.node_pool_min_count >= 2
    error_message = "node_pool_min_count must be at least 2 for production high availability."
  }
}

variable "node_pool_max_count" {
  description = "Maximum number of nodes in the node pool. Must be >= node_pool_min_count (cross-variable enforcement is done at plan time by AKS; HCL validation blocks cannot reference other variables)."
  type        = number
  default     = 3

  # NOTE: HCL validation blocks are restricted to referencing only the variable
  # being declared. Cross-variable comparisons like
  #   var.node_pool_max_count >= var.node_pool_min_count
  # are INVALID and cause `terraform validate` to fail with:
  #   "References to other variables are not allowed in validation block conditions."
  # The lower-bound check here catches obviously wrong single-variable values;
  # the max >= min constraint is enforced implicitly by the AKS API at apply time.
  validation {
    condition     = var.node_pool_max_count >= 1
    error_message = "node_pool_max_count must be at least 1. Ensure it is also >= node_pool_min_count (validated by AKS API at apply time)."
  }
}

variable "api_server_authorized_ip_ranges" {
  description = "CIDR ranges allowed to reach the AKS API server. Empty list = unrestricted (not recommended for production). Set to your CI/CD agent egress IPs and bastion/operator ranges."
  type        = list(string)
  default     = []
}

# Monitoring Configuration
variable "log_retention_days" {
  description = "Log retention period in days. 90-day minimum is recommended for production audit and compliance. Valid range: 30–730."
  type        = number
  default     = 90

  validation {
    condition     = var.log_retention_days >= 30 && var.log_retention_days <= 730
    error_message = "log_retention_days must be between 30 and 730."
  }
}
