# CloudTasker – Simulated GCP-Based Async Job Queue System

CloudTasker is a cloud-native asynchronous task queue system built to demonstrate scalable, fault-tolerant, and observable backend architecture using modern cloud technologies.
**Note:** This project **simulates integration with Google Cloud Platform (GCP)** for demonstration and educational purposes. It does **not actually deploy** or bill GCP resources, but reflects a real-world cloud-ready design.

---

## Features

*  **Pub/Sub Simulation**: Job queue modeled after Google Cloud Pub/Sub.
*  **Worker Service**: Asynchronous workers consume and process tasks with retry/backoff.
*  **Redis Caching**: Simulated fast caching layer for stateful processing.
*  **PostgreSQL Storage**: Persistent storage layer for task metadata.
*  **REST & gRPC APIs**: Supports both API paradigms for robust communication.
*  **GKE / Cloud Run Compatible**: Kubernetes-ready with containerized microservices.
*  **CI/CD with GitHub Actions**: Linting, type-checking, tests, and builds.
*  **Observability**: Structured logging, error handling, and monitoring hooks.

---

## Project Structure

```
CloudTasker_GCP/
├── api/                # REST & gRPC APIs
│   ├── python/         # Flask app (REST), protobuf, GCP Pub/Sub client
│   └── Dockerfile
├── worker/             # Async job processor
│   ├── python/         # Python task worker, DB, Redis logic
│   └── Dockerfile
├── infra/              # Terraform config (simulated GCP infra)
├── protos/             # Protobuf definitions for gRPC
├── .github/workflows/  # GitHub Actions (CI/CD)
├── docker-compose.yml  # Local dev with Redis, Postgres
└── README.md
```

---

## Local Development Setup

### Prerequisites

* Docker & Docker Compose
* Python 3.9+

### 1. Clone the repo

```bash
git clone https://github.com/kowstav/CloudTasker_GCP.git
cd CloudTasker_GCP
```

### 2. Start local services

```bash
docker-compose up --build
```

### 3. API & Worker

* REST API: [http://localhost:5000](5000)
* gRPC API: Port `50051` (localhost)
* Redis: Port `6379`
* PostgreSQL: Port `5432`

---

## Simulated Cloud Architecture

CloudTasker simulates a real GCP deployment:

| Component          | Simulated In              | GCP Equivalent           |
| ------------------ | ------------------------- | ------------------------ |
| Pub/Sub            | Python client & queues    | Google Cloud Pub/Sub     |
| API Gateway + Auth | Flask + routes            | API Gateway + IAM        |
| Redis              | Docker Redis              | Memorystore              |
| PostgreSQL         | Docker Postgres           | Cloud SQL                |
| gRPC Services      | Python + Protobuf         | Cloud Run / GKE Services |
| Infrastructure     | Terraform config (infra/) | GCP Resource Manager     |

This design lets you demonstrate cloud-native readiness without incurring GCP costs.

---

## CI/CD

GitHub Actions handles:

* `mypy` type checking
* `flake8` linting
* `black` formatting
* `pytest` for tests

To run locally:

```bash
make lint
make typecheck
make test
```

---

## API Example (REST)

```http
POST /enqueue-task
Content-Type: application/json

{
  "task_type": "send_email",
  "payload": {
    "to": "test@example.com",
    "subject": "Welcome!",
    "body": "Hello from CloudTasker!"
  }
}
```

---

## Testing

```bash
pytest
```

Tests include:

* Task enqueuing and dequeueing
* Worker retry logic
* Integration with Redis/Postgres

---

## Technologies

* Python
* Flask, gRPC, Protobuf
* Redis, PostgreSQL
* Docker, GitHub Actions
* Terraform (simulated GCP)
* Logging with `python-json-logger`

---

## Author

**Kowstav**
---

## 📄 License

[Apache 2.0]
