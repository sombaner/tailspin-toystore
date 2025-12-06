# Terraform Module Contract: Monitoring

**Module Path**: `infra/modules/monitoring/`  
**Purpose**: Provision Log Analytics workspace and Application Insights for observability

## Module Interface

### Required Inputs

| Variable | Type | Description | Constraints |
|----------|------|-------------|-------------|
| `resource_group_name` | string | Name of the resource group | Must exist |
| `location` | string | Azure region | Must be "centralindia" |
| `workspace_name` | string | Log Analytics workspace name | 4-63 chars |
| `appinsights_name` | string | Application Insights name | 1-255 chars |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `retention_in_days` | number | 30 | Log retention period |
| `tags` | map(string) | {} | Resource tags |

### Outputs

| Output | Type | Description | Usage |
|--------|------|-------------|-------|
| `workspace_id` | string | Log Analytics workspace resource ID | For AKS monitoring |
| `workspace_key` | string (sensitive) | Workspace shared key | For agent configuration |
| `appinsights_instrumentation_key` | string (sensitive) | Application Insights key | For application SDK |
| `appinsights_connection_string` | string (sensitive) | Connection string | For application SDK |

## Configuration Specifications

```hcl
resource "azurerm_log_analytics_workspace" "logs" {
  name                = var.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days
  
  tags = merge(
    var.tags,
    {
      ManagedBy = "Terraform"
      Component = "Monitoring"
    }
  )
}

resource "azurerm_application_insights" "appinsights" {
  name                = var.appinsights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.logs.id
  
  tags = var.tags
}
```

## Usage Example

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_name      = "log-tailspin-prod"
  appinsights_name    = "appi-tailspin-prod"
  retention_in_days   = 30
  
  tags = local.common_tags
}

# Configure AKS monitoring
module "aks" {
  source = "./modules/aks"
  log_analytics_workspace_id = module.monitoring.workspace_id
  # ... other inputs
}
```
