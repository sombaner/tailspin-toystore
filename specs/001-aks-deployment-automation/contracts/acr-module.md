# Terraform Module Contract: Azure Container Registry

**Module Path**: `infra/modules/acr/`  
**Purpose**: Provision Azure Container Registry for storing Docker container images

## Module Interface

### Required Inputs

| Variable | Type | Description | Constraints |
|----------|------|-------------|-------------|
| `resource_group_name` | string | Name of the resource group | Must exist before module call |
| `location` | string | Azure region | Must be "centralindia" |
| `acr_name` | string | Name of the container registry | 5-50 chars, alphanumeric only, globally unique |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `sku` | string | "Premium" | ACR SKU (Basic, Standard, Premium) |
| `admin_enabled` | bool | false | Enable admin user (not recommended) |
| `tags` | map(string) | {} | Resource tags |

### Outputs

| Output | Type | Description | Usage |
|--------|------|-------------|-------|
| `acr_id` | string | ACR resource ID | For role assignments |
| `acr_name` | string | ACR name | For docker login commands |
| `acr_login_server` | string | ACR login server URL | For image tags (e.g., acr.azurecr.io) |
| `acr_admin_username` | string (sensitive) | Admin username | Not used (admin disabled) |
| `acr_admin_password` | string (sensitive) | Admin password | Not used (admin disabled) |

## Configuration Specifications

```hcl
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  admin_enabled       = var.admin_enabled
  
  # Premium SKU features
  dynamic "georeplications" {
    for_each = var.sku == "Premium" ? var.geo_replications : []
    content {
      location = georeplications.value
      tags     = var.tags
    }
  }
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Component = "ACR"
    }
  )
}
```

## Validation Rules

```hcl
variable "acr_name" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9]{5,50}$", var.acr_name))
    error_message = "ACR name must be 5-50 alphanumeric characters (no hyphens or underscores)."
  }
}

variable "sku" {
  type = string
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "SKU must be Basic, Standard, or Premium."
  }
}

variable "location" {
  type = string
  validation {
    condition     = var.location == "centralindia"
    error_message = "ACR must be deployed in Central India region per requirement."
  }
}
```

## Usage Example

```hcl
module "acr" {
  source = "./modules/acr"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  acr_name            = "acrtailspin"  # Must be globally unique
  sku                 = "Premium"       # Required for vulnerability scanning
  admin_enabled       = false           # Use managed identity instead
  
  tags = {
    Environment = "production"
    Project     = "Tailspin"
  }
}

# Use in Docker build workflow
output "acr_login_server" {
  value = module.acr.acr_login_server
  # Output: acrtailspin.azurecr.io
}
```

## Security Considerations

- **Admin Access Disabled**: Uses managed identity for authentication (Constitution compliant)
- **Premium SKU**: Required for vulnerability scanning integration
- **RBAC Only**: No username/password credentials
- **Private Endpoints**: Not configured (future enhancement for production)

## Post-Deployment Actions

1. **Verify ACR creation**:
   ```bash
   az acr show --name acrtailspin --resource-group rg-sb-aks-01
   ```

2. **Create repositories** (automatic on first push):
   ```bash
   docker tag tailspin-server:latest acrtailspin.azurecr.io/tailspin-server:v1.0.0
   docker push acrtailspin.azurecr.io/tailspin-server:v1.0.0
   ```

3. **Verify managed identity access** (done by RBAC module):
   ```bash
   az role assignment list --scope $(az acr show -n acrtailspin --query id -o tsv)
   ```
