# RBAC Module - AKS to ACR Managed Identity Role Assignment

# Assign AcrPull role to AKS kubelet managed identity
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = var.aks_kubelet_identity_object_id
  role_definition_name             = "AcrPull"
  scope                            = var.acr_id
  skip_service_principal_aad_check = true
}
