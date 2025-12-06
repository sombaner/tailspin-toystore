# RBAC Module Outputs

output "role_assignment_id" {
  description = "Role assignment resource ID"
  value       = azurerm_role_assignment.aks_acr_pull.id
}
