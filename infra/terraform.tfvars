# Terraform Variable Values for Tailspin AKS Deployment
# Central India region deployment as per requirements
#
# IMPORTANT: Do NOT add secrets or credentials to this file.
# This file is committed to version control.
# Sensitive values must be passed via environment variables (TF_VAR_*)
# or injected by the CI/CD pipeline at runtime.

environment         = "prod"
location            = "centralindia"
resource_group_name = "rg-tailspin-prod"
project_name        = "tailspin"
owner               = "DevOps Team"
cost_center         = "Engineering"

# Networking
vnet_address_space        = ["10.0.0.0/16"]
aks_subnet_address_prefix = "10.0.1.0/24"

# AKS Configuration
# Pin to an EXACT patch version to prevent state drift.
# When Azure auto-patches the cluster (e.g. from 1.28 → 1.28.5), a partial
# version string causes every subsequent `terraform plan` to show a spurious diff.
# Check available versions: az aks get-versions --location centralindia --output table
kubernetes_version   = "1.28.5"
node_pool_vm_size    = "Standard_D2s_v3"
node_pool_min_count  = 2
node_pool_max_count  = 3

# API server access restriction
# SECURITY REQUIRED: An empty list allows ALL IPs on the internet to reach the
# Kubernetes API server. This MUST be populated before production deployment.
# Populate with:
#   - CI/CD agent egress IPs (GitHub-hosted runner ranges or self-hosted agent IPs)
#   - Bastion / operator workstation CIDRs
#   - VNet NAT gateway public IP (if using NAT for outbound)
# Example:
#   api_server_authorized_ip_ranges = ["203.0.113.10/32", "198.51.100.0/24"]
#
# Obtain GitHub Actions IP ranges: https://api.github.com/meta  (actions key)
# WARNING: Leaving this empty in production violates CIS AKS Benchmark 6.6.1.
api_server_authorized_ip_ranges = []  # TODO(security): Replace [] with real CIDR list before production deploy

# Monitoring — 90 days minimum for production audit/compliance
log_retention_days = 90
