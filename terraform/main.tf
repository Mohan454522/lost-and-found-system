# Configure providers
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.16.1"
    }
  }
}

provider "azurerm" {
  features {}
}

# Create Azure resource group
resource "azurerm_resource_group" "main" {
  name     = "mohan-lost-found-rg"
  location = "East US"
}

# Create AKS Kubernetes cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "mohan-aks-cluster"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "mohanaks"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Production"
    Project     = "Lost-Found-System"
  }
}

# Configure Kubernetes provider to use our AKS cluster
provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.main.kube_config.0.host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.cluster_ca_certificate)
}

# Deploy your application to Kubernetes
resource "kubernetes_deployment" "lost_found_app" {
  metadata {
    name = "lost-found-app"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "lost-found-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "lost-found-app"
        }
      }

      spec {
        container {
          image = "ghcr.io/mohan454522/lost-found-app:latest"
          name  = "lost-found-app"

          port {
            container_port = 5000
          }

          env {
            name  = "DATABASE_URL"
            value = "sqlite:///lost_found.db"
          }

          env {
            name  = "SECRET_KEY"
            value = "production-secret-key"
          }
        }
      }
    }
  }

  depends_on = [azurerm_kubernetes_cluster.main]
}

resource "kubernetes_service" "lost_found_service" {
  metadata {
    name = "lost-found-service"
  }

  spec {
    selector = {
      app = kubernetes_deployment.lost_found_app.spec.0.template.0.metadata.0.labels.app
    }

    port {
      port        = 80
      target_port = 5000
    }

    type = "LoadBalancer"
  }

  depends_on = [kubernetes_deployment.lost_found_app]
}

# Output the public IP
output "application_url" {
  value = "http://${kubernetes_service.lost_found_service.status.0.load_balancer.0.ingress.0.ip}"
}