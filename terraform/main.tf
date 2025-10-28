
# Configure Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Create resource group
resource "azurerm_resource_group" "main" {
  name     = "mohan-lost-found-rg"
  location = "East US"
}

# Create Container App Environment
resource "azurerm_container_app_environment" "main" {
  name                = "lost-found-environment"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Create Container App
resource "azurerm_container_app" "main" {
  name                         = "lost-found-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "lost-found-app"
      image  = "ghcr.io/mohan454522/lost-found-app:latest"
      cpu    = 1.0
      memory = "2Gi"

      env {
        name  = "DATABASE_URL"
        value = "sqlite:///lost_found.db"
      }
      env {
        name  = "SECRET_KEY"
        value = "terraform-production-2024"
      }
      env {
        name  = "FLASK_ENV"
        value = "production"
      }
      env {
        name  = "FLASK_APP"
        value = "run.py"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 5000
    traffic_weight {
      percentage = 100
      latest_revision = true
    }
  }

  tags = {
    Environment = "Production"
    Project     = "Lost-Found-System"
  }
}

# Output the application URL
output "application_url" {
  value = "https://${azurerm_container_app.main.ingress.0.fqdn}"
}