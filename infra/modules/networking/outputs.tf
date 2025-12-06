# Networking Module Outputs

output "vnet_id" {
  description = "Virtual Network resource ID"
  value       = azurerm_virtual_network.main.id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = azurerm_virtual_network.main.name
}

output "aks_subnet_id" {
  description = "AKS subnet resource ID"
  value       = azurerm_subnet.aks.id
}

output "aks_subnet_address_prefix" {
  description = "AKS subnet address prefix"
  value       = azurerm_subnet.aks.address_prefixes[0]
}
