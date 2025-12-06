# Terraform Variable Values for Tailspin AKS Deployment
# Central India region deployment as per requirements

environment         = "prod"
location            = "centralindia"
resource_group_name = "rg-sb-aks-01"
project_name        = "tailspin"
owner               = "DevOps Team"
cost_center         = "Engineering"

# Networking
vnet_address_space        = ["10.0.0.0/16"]
aks_subnet_address_prefix = "10.0.1.0/24"

# AKS Configuration
kubernetes_version   = "1.28"
node_pool_vm_size    = "Standard_D2s_v3"
node_pool_min_count  = 1
node_pool_max_count  = 3

# Monitoring
log_retention_days = 30
