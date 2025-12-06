# Terraform Module Contract: Networking

**Module Path**: `infra/modules/networking/`  
**Purpose**: Provision Virtual Network and subnets for AKS cluster

## Module Interface

### Required Inputs

| Variable | Type | Description | Constraints |
|----------|------|-------------|-------------|
| `resource_group_name` | string | Name of the resource group | Must exist before module call |
| `location` | string | Azure region | Must be "centralindia" |
| `vnet_name` | string | Virtual network name | 2-64 chars, alphanumeric and hyphens |
| `vnet_address_space` | list(string) | VNet CIDR blocks | Must not overlap with existing networks |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aks_subnet_address_prefix` | string | "10.0.1.0/24" | AKS subnet CIDR block |
| `tags` | map(string) | {} | Resource tags |

### Outputs

| Output | Type | Description | Usage |
|--------|------|-------------|-------|
| `vnet_id` | string | Virtual network resource ID | For subnet associations |
| `vnet_name` | string | Virtual network name | For documentation |
| `aks_subnet_id` | string | AKS subnet resource ID | For AKS cluster node pool |
| `aks_subnet_address_prefix` | string | AKS subnet CIDR | For network planning |

## Configuration Specifications

```hcl
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = var.vnet_address_space
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Component = "Networking"
    }
  )
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.aks_subnet_address_prefix]
}
```

## Usage Example

```hcl
module "networking" {
  source = "./modules/networking"
  
  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  vnet_name             = "vnet-tailspin-prod"
  vnet_address_space    = ["10.0.0.0/16"]
  aks_subnet_address_prefix = "10.0.1.0/24"
  
  tags = local.common_tags
}

# Pass subnet to AKS module
module "aks" {
  source    = "./modules/aks"
  subnet_id = module.networking.aks_subnet_id
  # ... other inputs
}
```
