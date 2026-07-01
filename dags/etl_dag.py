from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl_incremental import run_incremental_etl

import psycopg2


def log_row_count():

    conn = psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        dbname="postgres",
        user="postgres",
        password="amulya"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM analytics_db.sales_summary
    """)

    count = cur.fetchone()[0]

    print(f"Current row count: {count}")

    cur.close()
    conn.close()


default_args = {
    "owner": "amulya",
}

with DAG(
    dag_id="incremental_etl_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
) as dag:

    run_incremental_etl_task = PythonOperator(
        task_id="run_incremental_etl",
        python_callable=run_incremental_etl
    )

    log_row_count_task = PythonOperator(
        task_id="log_row_count",
        python_callable=log_row_count
    )

    run_incremental_etl_task >> log_row_count_task