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
  shared_access_key_enabled = true
}

resource "azurerm_storage_container" "container_raw" {
  name                  = "raw"
  storage_account_name  = azurerm_storage_account.storageaccount.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "container_final" {
  name                  = "final"
  storage_account_name  = azurerm_storage_account.storageaccount.name
  container_access_type = "private"
}

resource "azurerm_eventgrid_system_topic" "event_grid_topic" {
  name                = var.event_grid_topic_name
  location            = azurerm_storage_account.storageaccount.location
  resource_group_name = azurerm_resource_group.resource_group.name
  source_arm_resource_id = azurerm_storage_account.storageaccount.id
  topic_type          = "Microsoft.Storage.StorageAccounts"
}

resource "azurerm_eventgrid_event_subscription" "event_subscription_servicebus" {
  name                = "UploadEvent"
  scope               = azurerm_storage_account.storageaccount.id
  service_bus_queue_endpoint_id = azurerm_servicebus_queue.servicebus_queue.id
  included_event_types = ["Microsoft.Storage.BlobCreated"]
  event_delivery_schema = "EventGridSchema"
  retry_policy {
    max_delivery_attempts = 30
    event_time_to_live    = 1440
  }
}


resource "azurerm_role_assignment" "read_raw_container" {
  principal_id        = azurerm_user_assigned_identity.user_assigned_identity.principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope               = azurerm_storage_container.container_raw.resource_manager_id
}

resource "azurerm_role_assignment" "write_final_container" {
  principal_id        = azurerm_user_assigned_identity.user_assigned_identity.principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope               = azurerm_storage_container.container_final.resource_manager_id
}



