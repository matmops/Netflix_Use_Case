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
        value = "DefaultEndpointsProtocol=https;AccountName=${azurerm_storage_account.storageaccount.name};AccountKey=${azurerm_storage_account.storageaccount.primary_access_key};EndpointSuffix=core.windows.net"
      }


    }


    
    }
  }


resource "null_resource" "update_scale_rule" {
  provisioner "local-exec" {
    command = <<EOT
      az extension add --name containerapp --upgrade
      az containerapp update  --name ${azurerm_container_app.aca_netflix_use_case.name} --resource-group ${azurerm_resource_group.resource_group.name}  --scale-rule-name go-ahead --scale-rule-type azure-queue  --scale-rule-metadata accountName=${azurerm_storage_account.storageaccount.name} queueName=${azurerm_storage_queue.my_queue_for_the_aca_app.name} queueLength=1 --scale-rule-auth triggerParameter=connection secretRef=queue-connection-string  --scale-rule-identity ${azurerm_user_assigned_identity.user_assigned_identity.id}
    EOT
  }

    depends_on = [
    azurerm_container_app.aca_netflix_use_case,
    azurerm_storage_account.storageaccount,
    azurerm_storage_queue.my_queue_for_the_aca_app,
    azurerm_user_assigned_identity.user_assigned_identity,
    azurerm_servicebus_queue.servicebus_queue,
    azurerm_eventgrid_event_subscription.event_subscription_servicebus,
    azurerm_role_assignment.queue_role,
    
  ]
}
