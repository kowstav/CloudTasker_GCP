resource "google_service_account" "api_sa" {
  account_id   = "cloudtasker-api"
  display_name = "CloudTasker API Service Account"
}

resource "google_service_account" "worker_sa" {
  account_id   = "cloudtasker-worker"
  display_name = "CloudTasker Worker Service Account"
}

# IAM bindings
resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "worker_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.worker_sa.email}"
}