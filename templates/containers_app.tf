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
    value = "DefaultEndpointsProtocol=https;AccountName=${azurerm_storage_account.storageaccount.name};AccountKey=${azurerm_storage_account.storageaccount.primary_access_key};EndpointSuffix=core.windows.net"
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.user_assigned_identity.id]
  }

  template {

      min_replicas = 0
      max_replicas = 20

      
        azure_queue_scale_rule{
          name = "myscalingrule"
          queue_length = 1
          queue_name =  azurerm_storage_queue.my_queue_for_the_aca_app.name
          authentication {
            secret_name = "queue-connection-string"
            trigger_parameter = "connection"
          }
        }
      
      
    container {
      name   = "my-job-to-process-netflix"
      image  = "ghcr.io/matmops/netflix_use_case:latest"
      cpu    = 1
      memory = "2Gi"

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.user_assigned_identity.client_id
      }
        env {
        name  = "AZURE_STORAGE_QUEUE_NAME"
        value = azurerm_storage_queue.my_queue_for_the_aca_app.name
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
        name  = "AZURE_STORAGE_ACCOUNT_NAME"
        value = azurerm_storage_account.storageaccount.name
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


