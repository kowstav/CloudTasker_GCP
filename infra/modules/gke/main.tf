resource "google_pubsub_topic" "tasks" {
  name = "cloudtasker-tasks"
}

resource "google_pubsub_subscription" "worker" {
  name  = "cloudtasker-worker-sub"
  topic = google_pubsub_topic.tasks.name

  ack_deadline_seconds = 60

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}