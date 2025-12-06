# Terraform Module Contract: AKS Cluster

**Module Path**: `infra/modules/aks/`  
**Purpose**: Provision Azure Kubernetes Service cluster with automatic mode configuration

## Module Interface

### Required Inputs

| Variable | Type | Description | Constraints |
|----------|------|-------------|-------------|
| `resource_group_name` | string | Name of the resource group | Must exist before module call |
| `location` | string | Azure region | Must be "centralindia" |
| `cluster_name` | string | Name of the AKS cluster | 3-63 chars, alphanumeric and hyphens |
| `dns_prefix` | string | DNS prefix for cluster endpoint | 3-45 chars, alphanumeric and hyphens |
| `subnet_id` | string | Subnet ID for AKS nodes | Must be a valid subnet resource ID |
| `log_analytics_workspace_id` | string | Log Analytics workspace ID for monitoring | Must be a valid workspace resource ID |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kubernetes_version` | string | null | Kubernetes version (null = latest stable) |
| `sku_tier` | string | "Standard" | AKS SKU tier |
| `node_pool_vm_size` | string | "Standard_DS2_v2" | VM size for default node pool |
| `node_pool_min_count` | number | 1 | Minimum node count for auto-scaling |
| `node_pool_max_count` | number | 3 | Maximum node count for auto-scaling |
| `tags` | map(string) | {} | Resource tags |

### Outputs

| Output | Type | Description | Usage |
|--------|------|-------------|-------|
| `cluster_id` | string | AKS cluster resource ID | For role assignments, dependencies |
| `cluster_name` | string | AKS cluster name | For kubectl configuration |
| `cluster_fqdn` | string | Cluster FQDN | For API server access |
| `kubelet_identity_object_id` | string | Kubelet managed identity object ID | For ACR role assignment |
| `kube_config` | object (sensitive) | Kubeconfig for cluster access | For kubectl commands in CI/CD |
| `cluster_endpoint` | string | Kubernetes API server endpoint | For health checks |

## Resource Dependencies

**Requires**:
- Resource group (created before module)
- Virtual network with subnet
- Log Analytics workspace

**Creates**:
- `azurerm_kubernetes_cluster` resource
- System-assigned managed identity (automatic)

**Depends on** (implicit):
- Subnet must have sufficient IP space (/24 minimum)
- Log Analytics workspace must be in same region

## Configuration Specifications

### AKS Cluster Configuration

```hcl
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version
  
  # AKS Automatic mode (per requirement)
  sku_tier            = var.sku_tier
  automatic_upgrade_channel = "stable"
  
  default_node_pool {
    name                = "systempool"
    vm_size             = var.node_pool_vm_size
    enable_auto_scaling = true
    min_count           = var.node_pool_min_count
    max_count           = var.node_pool_max_count
    vnet_subnet_id      = var.subnet_id
    
    # Best practices
    os_disk_type        = "Managed"
    os_disk_size_gb     = 128
  }
  
  # Managed identity (required for ACR integration)
  identity {
    type = "SystemAssigned"
  }
  
  # Public cluster configuration (per requirement)
  api_server_access_profile {
    authorized_ip_ranges = []  # Empty = public access
  }
  
  # Monitoring integration
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }
  
  # Network profile
  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    network_policy    = "azure"
  }
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Component = "AKS"
    }
  )
}
```

## Validation Rules

### Pre-Deployment Validation

```hcl
# Validate location
variable "location" {
  type = string
  validation {
    condition     = var.location == "centralindia"
    error_message = "AKS cluster must be deployed in Central India region per requirement."
  }
}

# Validate node pool sizing
variable "node_pool_min_count" {
  type = number
  validation {
    condition     = var.node_pool_min_count >= 1 && var.node_pool_min_count <= var.node_pool_max_count
    error_message = "Min count must be >= 1 and <= max count."
  }
}

variable "node_pool_max_count" {
  type = number
  validation {
    condition     = var.node_pool_max_count >= 1 && var.node_pool_max_count <= 10
    error_message = "Max count must be between 1 and 10."
  }
}
```

## Usage Example

```hcl
module "aks" {
  source = "./modules/aks"
  
  # Required inputs
  resource_group_name         = azurerm_resource_group.main.name
  location                    = azurerm_resource_group.main.location
  cluster_name                = "aks-tailspin-prod"
  dns_prefix                  = "tailspin"
  subnet_id                   = module.networking.aks_subnet_id
  log_analytics_workspace_id  = module.monitoring.workspace_id
  
  # Optional inputs
  node_pool_vm_size  = "Standard_DS2_v2"
  node_pool_min_count = 1
  node_pool_max_count = 3
  
  tags = {
    Environment = "production"
    Project     = "Tailspin"
    Owner       = "DevOps Team"
    CostCenter  = "Engineering"
  }
}

# Use outputs
output "aks_cluster_name" {
  value = module.aks.cluster_name
}

# Configure kubectl in GitHub Actions
resource "null_resource" "configure_kubectl" {
  provisioner "local-exec" {
    command = "az aks get-credentials --resource-group ${module.aks.cluster_name} --name ${module.aks.cluster_name}"
  }
}
```

## Lifecycle Considerations

### Creation Time
- **Expected**: 12-15 minutes
- **Factors**: Region load, node provisioning, networking setup

### Update Operations
- **Node pool scaling**: 3-5 minutes per node
- **Kubernetes version upgrade**: 15-30 minutes (depends on node count)
- **Configuration changes**: 2-5 minutes

### Deletion
- **Expected**: 10-15 minutes
- **Note**: Requires manual approval (safety mechanism)

## Security Considerations

- **Managed Identity**: Automatic creation eliminates credential management
- **Public Cluster**: API server publicly accessible (per requirement, not recommended for production)
- **RBAC**: Azure RBAC enabled by default
- **Network Policy**: Azure Network Policy enabled for pod-to-pod security
- **Monitoring**: OMS agent sends logs to Log Analytics for audit trail

## Post-Deployment Actions

After module apply:

1. **Verify cluster status**:
   ```bash
   az aks show --resource-group rg-sb-aks-01 --name aks-tailspin-prod --query "powerState.code"
   # Expected: "Running"
   ```

2. **Get credentials**:
   ```bash
   az aks get-credentials --resource-group rg-sb-aks-01 --name aks-tailspin-prod --overwrite-existing
   ```

3. **Verify connectivity**:
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

4. **Check managed identity**:
   ```bash
   az aks show --resource-group rg-sb-aks-01 --name aks-tailspin-prod --query "identityProfile.kubeletidentity.objectId" -o tsv
   ```

## Troubleshooting

### Common Issues

**Issue**: Cluster creation fails with "subnet too small"  
**Resolution**: Ensure subnet has /24 or larger CIDR block

**Issue**: Node provisioning stuck  
**Resolution**: Check Azure quota limits for VM cores in region

**Issue**: Cannot connect to API server  
**Resolution**: Verify public IP allowed in network policies (for restricted networks)

## References

- [AKS Terraform Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster)
- [AKS Automatic Mode Documentation](https://learn.microsoft.com/azure/aks/automatic)
- [AKS Best Practices](https://learn.microsoft.com/azure/aks/best-practices)
