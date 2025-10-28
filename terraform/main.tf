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

# Create Container Instance
resource "azurerm_container_group" "lost_found_app" {
  name                = "lost-found-app"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = "mohan-lost-found"
  os_type             = "Linux"
  restart_policy      = "Always"

  container {
    name   = "lost-found-app"
    image  = "ghcr.io/mohan454522/lost-found-app:latest"
    cpu    = "1.0"
    memory = "2.0"

    ports {
      port     = 80    # External port 80
      protocol = "TCP"
    }

    environment_variables = {
      DATABASE_URL = "sqlite:///lost_found.db"
      SECRET_KEY   = "terraform-production-2024"
      FLASK_ENV    = "production"
      FLASK_APP    = "run.py"
    }
  }

  tags = {
    Environment = "Production"
    Project     = "Lost-Found-System"
  }
}

# Output the application URL
output "application_url" {
  value = "http://${azurerm_container_group.lost_found_app.fqdn}"
}