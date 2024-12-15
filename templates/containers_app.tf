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
    value = azurerm_storage_account.storageaccount.primary_access_key
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.user_assigned_identity.id]
  }

  template {

      min_replicas = 0
      max_replicas = 20



    custom_scale_rule {
      custom_rule_type = "azure-queue"
        name         = "queue-scaling-rule"
 

        metadata = {
          accountName = azurerm_storage_account.storageaccount.name
          queueName   = azurerm_storage_queue.my_queue_for_the_aca_app.name
          queueLength = "1"
          connectionFromEnv = "queue-connection-string"
        }

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
        name  = "AZURE_STORAGE_CONNECTION_STRING"
        value = "secretref:queue-connection-string"
      }


    }


    
    }
  }
 resource "azurerm_role_assignment" "queue_role_assignment" {
  principal_id         = azurerm_user_assigned_identity.user_assigned_identity.client_id
  role_definition_name = "Storage Queue Data Contributor"
  scope                = azurerm_storage_queue.my_queue_for_the_aca_app.resource_manager_id
}
 