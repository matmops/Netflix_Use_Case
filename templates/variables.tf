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
  default = "UploadEvent"
}

variable "storage_account_id" {
  type    = string
  default = "/subscriptions/1d874ea7-d53d-4cef-9987-572bff2963ba/resourceGroups/rg-netflix-usecase/providers/Microsoft.Storage/StorageAccounts/container_raw"
}

variable "service_bus_namespace_name" {
  type    = string
  default = "NetflixServiceBusNamespace"
}

variable "service_bus_queue_name" {
  type    = string
  default = "netflixbusqueue"
}