# main.tf

terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

################################################################################
# Input variable definitions
################################################################################

variable "deployment_name" {
  description = "Name of the deployment."
  type        = string
  default     = "testservice"
}

variable "image_tag" {
  description = "full image gcr image tag"
  type        = string
}

variable "image_repository" {
  description = "gcr repository name"
  type        = string
}

variable "image_version" {
  description = "gcr image version"
  type        = string
}

variable "project_id" {
  description = "GCP project to use for creating deployment."
  type        = string
}

variable "region" {
  description = "GCP region to use for deployments."
  type        = string
  default     = "us-central1"
}

variable "port" {
  description = "Port which the contiainer exposes"
  type        = string
  default     = "3000"
}

variable "min_instances" {
  description = "Minimum number of instances."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances."
  type        = number
  default     = 1
}

variable "memory" {
  description = "Memory for each instance"
  type        = string
  default     = "512M"
}

variable "cpu" {
  description = "CPU cores for each instance"
  type        = number
  default     = 1
}

################################################################################
# Resource definitions
################################################################################

# Enables the Cloud Run API
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
  project = var.project_id

  disable_on_destroy = true
}


# Data source for container registry image
data "google_container_registry_image" "bento_service" {
  name = var.image_repository
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  name     = "${var.deployment_name}-cloud-run-service"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.min_instances
        "autoscaling.knative.dev/maxScale" = var.max_instances
      }
    }

    spec {
      containers {
        image = "${data.google_container_registry_image.bento_service.image_url}:${var.image_version}"
        env {
          name  = "BENTOML_PORT"
          value = var.port
        }
        ports {
          container_port = var.port
        }
        resources {
          limits = {
            memory = var.memory
            cpu    = var.cpu
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }


  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api]
}

# Allow unauthenticated users to invoke the service
resource "google_cloud_run_service_iam_member" "run_all_users" {
  service  = google_cloud_run_service.run_service.name
  location = google_cloud_run_service.run_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

################################################################################
# Output value definitions
################################################################################

output "endpoint" {
  description = "Base URL for API Gateway stage."

  value = google_cloud_run_service.run_service.status[0].url
}

output "ImageUrl" {
  description = "Image URL for the image"
  value       = data.google_container_registry_image.bento_service.image_url
}
