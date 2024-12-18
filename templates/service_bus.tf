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

resource "azurerm_servicebus_queue" "servicebus_queue_log" {
  name         = "${var.service_bus_queue_name}_log"
  namespace_id = azurerm_servicebus_namespace.servicebus_namespace.id
}


resource "azurerm_servicebus_namespace_authorization_rule" "queue_listener" {
  name                = "listener-policy"
  namespace_id     = azurerm_servicebus_namespace.servicebus_namespace.id

  listen              = true
  send                = true
  manage              = true
}


resource "azurerm_role_assignment" "service_bus_queue_role" {
    scope                = azurerm_servicebus_namespace.servicebus_namespace.id
  role_definition_name = "Azure Service Bus Data Receiver"
  principal_id         = azurerm_user_assigned_identity.user_assigned_identity.principal_id
}


resource "azurerm_role_assignment" "service_bus_queue_role_for_log" {
    scope                = azurerm_servicebus_namespace.servicebus_namespace.id
  role_definition_name = "Azure Service Bus Data Sender"
  principal_id         = azurerm_user_assigned_identity.user_assigned_identity.principal_id
}

