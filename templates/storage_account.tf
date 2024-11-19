resource "random_integer" "id" {
  min = 100
  max = 999
}

resource "azurerm_storage_account" "storageaccount" {
  name                     = "netflixsa${random_integer.id.result}"
  resource_group_name      = azurerm_resource_group.resource_group.name
  location                 = azurerm_resource_group.resource_group.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container_raw" {
  name                  = "raw"
  storage_account_name    = azurerm_storage_account.storageaccount.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "container_final" {
  name                  = "final"
  storage_account_name    = azurerm_storage_account.storageaccount.name
  container_access_type = "private"
}

resource "azurerm_eventgrid_system_topic" "event_grid_topic" {
  name                = var.event_grid_topic_name
  location            = "northeurope"
  resource_group_name = azurerm_resource_group.resource_group.name
  source_arm_resource_id = azurerm_storage_container.container_raw.id
  topic_type          = "Microsoft.Storage.StorageAccounts"
}

resource "azurerm_eventgrid_event_subscription" "event_subscription" {
  name                = "UploadEvent"
  scope               = azurerm_eventgrid_system_topic.event_grid_topic.id
  service_bus_queue_endpoint_id = "${var.service_bus_namespace_id}/queues/netflixbusqueue"
  included_event_types = ["Microsoft.Storage.BlobCreated"]
  event_delivery_schema = "EventGridSchema"
  retry_policy {
    max_delivery_attempts = 30
    event_time_to_live    = 1440
  }
}