variable "location" {
  type    = string
  default = "francecentral"
}

variable "resource_group_name" {
  type    = string
  default = "rg-netflix-usecase"
}

variable "event_grid_topic_name" {
  type    = string
  default = "AVIBlobUploads"
}

variable "storage_account_id" {
  type    = string
  default = "/subscriptions/1d874ea7-d53d-4cef-9987-572bff2963ba/resourceGroups/neflix_use_case/providers/Microsoft.Storage/StorageAccounts/inputcontainerfornetflix"
}

variable "service_bus_namespace_id" {
  type    = string
  default = "/subscriptions/1d874ea7-d53d-4cef-9987-572bff2963ba/resourceGroups/neflix_use_case/providers/Microsoft.ServiceBus/namespaces/NetflixNameSpace"
}