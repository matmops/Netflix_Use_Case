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