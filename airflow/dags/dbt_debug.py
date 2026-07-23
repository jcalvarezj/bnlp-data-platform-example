import os

from airflow.sdk import task, dag

from constants import DBT_PATH

@dag
def dbt_debug_dag(): # Just for testing dbt-db connection
    @task.bash
    def dbt_debug_task():
        return "cd /opt/dbt_etl && dbt debug"

    dbt_debug = dbt_debug_task()

    dbt_debug

dbt_debug_dag()
