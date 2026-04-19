# Monitoring Module - Log Analytics and Application Insights

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days

  tags = var.tags

  # SAFETY: Destroying the workspace permanently deletes all ingested logs and
  # breaks the OMS agent integration on every AKS cluster pointing to it.
  # Recovery requires re-ingestion and re-linking all connected resources.
  lifecycle {
    prevent_destroy = true
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = var.appinsights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = var.tags

  # SAFETY: Destroying Application Insights permanently deletes the
  # instrumentation key and all historical telemetry stored in the workspace.
  lifecycle {
    prevent_destroy = true
  }
}
