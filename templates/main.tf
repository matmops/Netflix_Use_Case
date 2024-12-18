# Resource Group
resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name
  location = var.location
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
}

# Subnet
resource "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.resource_group.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# User-Assigned Identity
resource "azurerm_user_assigned_identity" "user_assigned_identity" {
  name                = "IdentityForVmToRightAndRead"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = var.location
}

# Storage Account for the Function App
resource "azurerm_storage_account" "function_storage" {
  name                     = "funcstorage${random_id.storage_suffix.hex}"
  resource_group_name      = azurerm_resource_group.resource_group.name
  location                 = azurerm_resource_group.resource_group.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Random ID for Uniqueness
resource "random_id" "storage_suffix" {
  byte_length = 4
}

// App Service Plan for Function App (Dynamic Consumption Plan)
resource "azurerm_app_service_plan" "function_plan" {
  name                = "dlq-processor-plan"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  kind                = "FunctionApp"
  reserved            = true  # Reserved is required for Linux
  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

// Azure Function App to process DLQ
resource "azurerm_linux_function_app" "function_app_dlq" {
  name                = "function-process"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  service_plan_id     = azurerm_app_service_plan.function_plan.id

  storage_account_name       = azurerm_storage_account.storageaccount_raw.name
  storage_account_access_key = azurerm_storage_account.storageaccount_raw.primary_access_key

  site_config {
    always_on        = false
    application_stack {
      python_version = "3.9"  # Specify built-in Python runtime
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"                = "python"
    "AzureWebJobs.ServiceBusConnectionString" = azurerm_servicebus_namespace_authorization_rule.queue_listener.primary_connection_string
    "queueName"                               = "${azurerm_servicebus_queue.servicebus_queue.name}/$DeadLetterQueue"
    "FUNCTIONS_EXTENSION_VERSION"             = "~4"
  }

  identity {
    type = "SystemAssigned"
  }
}

// Role Assignment for Service Bus Access
resource "azurerm_role_assignment" "function_servicebus_role" {
  scope                = azurerm_servicebus_namespace.servicebus_namespace.id
  role_definition_name = "Azure Service Bus Data Receiver"
  principal_id         = azurerm_linux_function_app.function_app_dlq.identity[0].principal_id
}
