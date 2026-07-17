import polars as pl
from airflow.sdk import dag, task, TriggerRule

from constants import (AIRFLOW_DB_CONN, AIRFLOW_DB_DW_CONN, PG_CONN_STR,
                       GET_WAREHOUSE_DB, CREATE_WAREHOUSE_DB, CREATE_RAW_SCHEMA)
from data_gen import (DataGen, UserGen, PurchaseGen, MerchantGen,
                      InstallmentGen, PaymentGen)
from logger import logger


def _generate_and_send_specific_data(data_gen: DataGen):
    logger.info(f"Generating {data_gen.table_prefix} data")
    data_df = data_gen.generate()
    logger.info(f"Generated {data_df.height} rows of {data_gen.table_prefix} data."
                + " Sending to DB...")
    data_gen.send_to_db(data_df)
    return data_df


@dag
def run_data_platform():
    @task.branch
    def should_create_db():
        try:
            wdb_df = pl.read_database_uri(
                GET_WAREHOUSE_DB,
                PG_CONN_STR,
                engine="adbc"
            )
            return "create_db" if wdb_df.height == 0 else "generate_and_send_data"
        except Exception as e:
            logger.exception(e)
            raise e

    @task.sql(conn_id=AIRFLOW_DB_CONN, autocommit=True)
    def create_db():
        logger.info("Creating warehouse database")
        return CREATE_WAREHOUSE_DB

    @task.sql(conn_id=AIRFLOW_DB_DW_CONN, autocommit=True)
    def create_raw_schema():
        logger.info("Creating raw schema")
        return CREATE_RAW_SCHEMA

    @task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def generate_and_send_data():
        _generate_and_send_specific_data(MerchantGen())

        user_df = _generate_and_send_specific_data(UserGen())
        user_ids = user_df["user_id"].to_list()

        purch_gen = PurchaseGen(user_ids)
        _generate_and_send_specific_data(purch_gen)

        purch_df = purch_gen.get_latest_n_rows(5)
        instlmt_gen = InstallmentGen(purch_df)
        _generate_and_send_specific_data(instlmt_gen)

        paid_instlmt_df = instlmt_gen.get_paid_installments()
        payment_gen = PaymentGen(paid_instlmt_df)
        _generate_and_send_specific_data(payment_gen)

        return {"status": "success"}

    should_create_db_task = should_create_db()
    create_db_task = create_db()
    create_raw_schema_task = create_raw_schema()
    generate_data_task = generate_and_send_data()

    should_create_db_task >> [create_db_task, generate_data_task]
    create_db_task >> create_raw_schema_task >> generate_data_task

run_data_platform()
