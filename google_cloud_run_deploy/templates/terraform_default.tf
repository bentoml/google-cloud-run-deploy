# main.tf

terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

provider "google" {
  project = var.project
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

variable "project" {
  description = "GCP project to use for creating deployment."
  type        = string
  default     = "bentoml-316710"
}

variable "region" {
  description = "GCP region to use for deployments."
  type        = string
  default     = "us-central1"
}


################################################################################
# Resource definitions
################################################################################

# Enables the Cloud Run API
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"

  disable_on_destroy = true
}

# make sure the container registry apis are also ennabled

# Data source for container registry image
data "google_container_registry_image" "bento_service" {
  name = "gcpimg"
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  name     = "${var.deployment_name}-cloud-run-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${data.google_container_registry_image.bento_service.image_url}:v1"
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

output "Endpoint" {
  description = "Base URL for API Gateway stage."

  value = google_cloud_run_service.run_service.status[0].url
}

output "ImageUrl" {
  description = "Image URL for the image"
  value       = data.google_container_registry_image.bento_service.image_url
}
