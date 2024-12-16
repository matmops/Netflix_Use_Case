resource "azurerm_servicebus_namespace" "servicebus_namespace" {
  name                = "Myservicebusfornetflix${random_integer.id.result}"
  location            = azurerm_resource_group.resource_group.location
  resource_group_name = azurerm_resource_group.resource_group.name
  sku                 = "Standard"
}

resource "azurerm_servicebus_queue" "servicebus_queue" {
  name         = var.service_bus_queue_name
  namespace_id = azurerm_servicebus_namespace.servicebus_namespace.id
}
