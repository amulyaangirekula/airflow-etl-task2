# Airflow ETL Task

## Project Overview

This repository contains an Apache Airflow project that defines and runs ETL pipelines using Docker Compose for local development. The DAGs implement incremental and full ETL workflows to extract data, transform it, and load it into the target destination.

## Repository Structure

- `docker-compose.yaml` — Docker Compose configuration to launch Airflow services for local development.
- `config/airflow.cfg` — Airflow configuration file used by the local deployment.
- `dags/` — Airflow DAG definitions and related ETL task code.
  - `etl_dag.py` — Primary ETL DAG (full or orchestrating workflow).
  - `etl_incremental.py` — Incremental ETL DAG used for delta updates.
- `logs/` — Airflow run logs (generated at runtime).
- `plugins/` — Custom Airflow plugins (if any).
- `.env` — Environment variables used by Docker Compose and Airflow (not checked in here).

## Architecture & Workflow

The DAGs are designed to be modular and idempotent. Typical steps in the ETL workflows:

1. Extract: read from a source (database, API, file storage).
2. Transform: apply business rules, cleaning, joins, and incremental logic.
3. Load: write to the destination system (database, data warehouse, or files).

Incremental runs rely on tracking a watermark (timestamp or numeric offset) so that only new or updated records are processed each run.

## Requirements

- Docker and Docker Compose (for local Airflow stack)
- Git (for source control)
- Python 3.8+ (for developing DAGs and local tooling)

## Quickstart (Local Development)

1. Copy environment variables into a `.env` file at the project root. You can use the provided `.env.example` if available.

2. Start the local Airflow stack:

```bash
docker-compose up -d
```

3. Open the Airflow web UI (usually at `http://localhost:8080`) to trigger or inspect DAG runs.

4. Trigger the DAGs from the UI or use the Airflow CLI inside the scheduler or webserver container.

## Environment Variables

Put any secrets or deployment-specific configuration in a `.env` file (not checked into git). Common variables include database connection URIs, credentials, and Airflow-specific settings used by `docker-compose.yaml`.

## Development

- Edit DAGs under the `dags/` directory. Airflow will automatically discover DAGs placed there.
- Use the `logs/` directory for debugging task runs; logs are also visible in the Airflow UI.
- For iterative development, restart or reload the scheduler/webserver containers when changing plugin or config code.

## Testing

- Unit tests: add pytest tests for operator logic or utility functions.
- Integration: run DAGs in a disposable local Airflow instance (Docker Compose) to validate end-to-end behavior.

## CI/CD and Deployment

This project can be deployed to a managed Airflow environment or a containerized Kubernetes-based Airflow deployment. For production, externalize secrets to a vault or a secrets manager, and configure scalable executors (Celery, KubernetesExecutor, or similar).

## Contributing

1. Fork the repo and create a branch for your feature or fix.
2. Add tests (where applicable) and run them locally.
3. Open a pull request with a clear description of changes and why they are needed.

## Troubleshooting

- If DAGs do not appear in the UI, verify that the files are syntactically valid and in the `dags/` directory.
- Check container logs (`docker-compose logs`) for errors during startup.

## Contact

If you have questions about the ETL logic or the DAGs, open an issue in this repository or contact the maintainer.

---

*Generated: Detailed README added for local development and collaborator guidance.*
