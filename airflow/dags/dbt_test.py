import os

from airflow.sdk import task, dag

from constants import DBT_PATH

@dag
def xxx_dag():
    @task.bash
    def yyy_task():

        return "cd /opt/dbt_etl && dbt debug"
        #return f"""cd $HOME && ls"""

    yyy = yyy_task()

    yyy

xxx_dag()
