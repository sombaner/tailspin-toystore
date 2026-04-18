# RBAC Module Variables

variable "aks_kubelet_identity_object_id" {
  description = "Object ID of AKS kubelet managed identity"
  type        = string
}

variable "acr_id" {
  description = "Azure Container Registry resource ID"
  type        = string
}
