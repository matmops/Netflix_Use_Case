resource "azurerm_log_analytics_workspace" "log_workspace_for_aca_netflix" {
  name                = "acctest-01"
  location            = azurerm_resource_group.resource_group.location
  resource_group_name = azurerm_resource_group.resource_group.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "aca_env" {
  name                       = "Env-aca-netflix"
  location                   = azurerm_resource_group.resource_group.location
  resource_group_name        = azurerm_resource_group.resource_group.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log_workspace_for_aca_netflix.id
}

resource "azurerm_container_app" "aca_netflix_use_case" {
  name                         = "aca-netflix-use-case-app"
  container_app_environment_id = azurerm_container_app_environment.aca_env.id
  resource_group_name          = azurerm_resource_group.resource_group.name
  revision_mode                = "Single"

  secret {
    name = "queue-connection-string"
    value = azurerm_servicebus_namespace_authorization_rule.queue_listener.primary_connection_string
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.user_assigned_identity.id]
  }

  

  template {

      min_replicas = 0
      max_replicas = 20
  
custom_scale_rule{
  name = "go-ahead"
  custom_rule_type = "azure-servicebus"
  metadata = {
    namespace = azurerm_servicebus_namespace.servicebus_namespace.name
    queueName = azurerm_servicebus_queue.servicebus_queue.name
    messageCount = 1
  }
  authentication {
    trigger_parameter = "connection"
    secret_name = "queue-connection-string"
  }
}

      
    
    container {
      name   = "my-job-to-process-netflix"
      image  = "ghcr.io/matmops/netflix_use_case_2:latest"
      cpu    = 1
      memory = "2Gi"

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.user_assigned_identity.client_id
      }

        env {
        name  = "AZURE_SERVICEBUS_NAME_SPACE"
        value = azurerm_servicebus_namespace.servicebus_namespace.name
      }

        env {
        name  = "AZURE_SERVICEBUS_QUEUE_NAME"
        value = azurerm_servicebus_queue.servicebus_queue.name
      }

        env {
        name  = "AZURE_STORAGE_ACCOUNT_NAME_RAW"
        value = azurerm_storage_account.storageaccount_raw.name
      }
              env {
        name  = "AZURE_STORAGE_ACCOUNT_NAME_FINAL"
        value = azurerm_storage_account.storageaccount_final.name
      }

              env {
        name  = "AZURE_BLOB_READ"
        value = azurerm_storage_container.container_raw.name
      }
              env {
        name  = "AZURE_BLOB_WRITE"
        value = azurerm_storage_container.container_final.name
      }

      
      


    }


    
    }
  }


