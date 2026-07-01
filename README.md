
# Airflow ETL Task — Project Timeline & Explanation

This repository contains a small Apache Airflow project created to implement, run, and debug ETL pipelines locally using Docker Compose. The goal of the project was to build a reproducible incremental ETL pipeline, capture run logs, and provide a configuration template so future contributors understand how to run and extend the system.

The sections below explain what was done, why, and where to look to understand each change. If you are reading this after cloning the repo, this file will tell you everything you need to run the stack, reproduce runs, and modify the ETL logic.

**What happened in this project (summary)**

- I scaffolded a Docker Compose-based Airflow development stack (see `docker-compose.yaml`) so the environment is self-contained and reproducible.
- I implemented two DAGs placed in `dags/`: a primary orchestration DAG (`etl_dag.py`) and an incremental DAG (`etl_incremental.py`). These implement extraction, transformation, and load steps, with incremental logic based on a watermark.
- Runtime logs are collected under `logs/` during development and are visible in the Airflow UI for each task run.
- This README was expanded to include a clear narrative and a `.env.example` file was added to show required environment variables and their purpose.

## Files Changed / Created

- `docker-compose.yaml`: defines Airflow services (webserver, scheduler, worker, database). Used for local development.
- `config/airflow.cfg`: Airflow configuration used by the containers (if you need to tune settings, edit this file).
- `dags/etl_dag.py`: main orchestrator DAG (full-run logic and orchestration of downstream tasks).
- `dags/etl_incremental.py`: incremental DAG implementing delta logic and watermark tracking.
- `logs/`: runtime logs generated when tasks run locally.
- `.env.example`: example environment variables (do NOT store secrets in repo; copy to `.env` and fill in real values).

## Detailed Explanation of the ETL Logic

- Extraction: the DAGs call Python tasks/operators that extract from the source system (e.g., a PostgreSQL database or an HTTP API). The extraction step writes a staging file or pushes results directly into an in-memory dataframe for transformation.
- Transformation: cleaning, type normalization, deduplication, and business-rule application occur here. The code is written to be idempotent — re-processing the same input should not create duplicates in the destination.
- Incremental Logic: `etl_incremental.py` uses a watermark column (timestamp or numeric ID). The DAG reads the last processed watermark (from a file, metastore, or target table) and fetches only records newer than that watermark. After a successful run, the watermark is updated.
- Load: writes transformed records into the destination (a database table or a file location). The loader uses transactional writes where possible and verifies row counts or checksums on success.

If you need the exact extraction source or destination endpoints, open the DAG files in `dags/` which contain inline configuration and comments describing expected connection URIs and table names.

## How to Run Locally (reproducible steps)

1. Copy `.env.example` to `.env` and fill in the real values (hostnames, credentials, connection strings). Do not commit real secrets.

```powershell
copy .env.example .env
```

2. Start the stack:

```bash
docker-compose up -d
```

3. Wait for containers to start, then open the Airflow UI at `http://localhost:8080`.

4. In the UI, enable and trigger `etl_incremental` or `etl_dag` to test runs. Inspect task logs from the UI or under `logs/`.

## Sample `.env` values and guidance

This repository contains `.env.example` which lists required variables and explains each one.

- Do not commit real credentials. Use this example as the template for your local `.env` file.
- If running in CI or production, inject these values from your secrets manager rather than committing them.

## Observability & Logs

- Task logs are available in the Airflow UI and under the `logs/` directory for offline inspection.
- If runs fail, check `docker-compose logs` for the scheduler or webserver and the individual task logs in the UI.

## How to Inspect What Changed (for reviewers)

- Review the DAGs in `dags/` for the ETL code paths and comments explaining sources, transformations, and destinations.
- Check `docker-compose.yaml` for service configuration and environment variable references.
- Use `git log --stat` to see the exact diffs and file additions made during this project.

## Example debugging commands

```bash
docker-compose logs -f webserver
docker-compose exec webserver airflow dags list
docker-compose exec webserver airflow tasks test etl_incremental extract_task 2026-06-22
```

## Next steps & recommendations

- Add unit tests for the transformation logic (pytest). Place tests under `tests/`.
- Add a small state store (database table or S3 file) to persist watermark progress in production.
- Add a CI check that lints DAGs and runs the transformation unit tests.

---

The repository now includes `.env.example` to help future developers know what to fill in. If you want, I can also create a small script to populate a local test database with sample data for end-to-end testing.

