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
  subscription_id = "1d874ea7-d53d-4cef-9987-572bff2963ba"
  tenant_id       = "d7c4eaa4-f23f-4da8-ac82-79a2732c514f"
}