import logging

from airflow.sdk import dag, task


logger = logging.getLogger("airflow.task")


@dag
def run_data_platform():
    @task
    def print_hello():
        logger.info("HELLO WORLD")
        return {"status": "success"}

    print_hello_task = print_hello()

    print_hello_task

run_data_platform()
