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

variable "service_bus_queue_name" {
  type    = string
  default = "netflixbusqueue"
}

variable "subscription_id" {
  type    = string
  default = "0c1d0bd5-b6f7-4edb-a81b-e7b93f18c776"
}

variable "tenant_id" {
  type    = string
  default = "ba196df7-d91c-4b26-a560-886da6630df7"
}

variable "vnet_name" {
  type    = string
  default = "netflix-vnet"
}

variable "subnet_name" {
  type    = string
  default = "default"
}