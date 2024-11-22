terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.9"
    }

    http = {
      source  = "hashicorp/http"
      version = "3.1.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  skip_provider_registration = false
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}