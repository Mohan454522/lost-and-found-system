terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.16.1"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

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
          image = "lost-found-app:latest"
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
}