# Terraform Outputs for Tailspin AKS Deployment

# Resource Group
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# AKS Cluster
output "aks_cluster_id" {
  description = "AKS cluster resource ID"
  value       = module.aks.cluster_id
}

output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = module.aks.cluster_name
}

output "aks_cluster_endpoint" {
  description = "AKS cluster API server endpoint"
  value       = module.aks.cluster_endpoint
}

output "aks_cluster_fqdn" {
  description = "AKS cluster FQDN"
  value       = module.aks.cluster_fqdn
}

output "aks_kube_config" {
  description = "Kubeconfig for AKS cluster access"
  value       = module.aks.kube_config
  sensitive   = true
}

# Azure Container Registry
output "acr_id" {
  description = "ACR resource ID"
  value       = module.acr.acr_id
}

output "acr_name" {
  description = "ACR name"
  value       = module.acr.acr_name
}

output "acr_login_server" {
  description = "ACR login server URL"
  value       = module.acr.acr_login_server
}

# Networking
output "vnet_id" {
  description = "Virtual Network resource ID"
  value       = module.networking.vnet_id
}

output "aks_subnet_id" {
  description = "AKS subnet resource ID"
  value       = module.networking.aks_subnet_id
}

# Monitoring
output "log_analytics_workspace_id" {
  description = "Log Analytics workspace resource ID"
  value       = module.monitoring.workspace_id
}

output "app_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.appinsights_instrumentation_key
  sensitive   = true
}

output "app_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.monitoring.appinsights_connection_string
  sensitive   = true
}
