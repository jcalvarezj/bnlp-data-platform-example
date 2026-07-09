from airflow.sdk import dag, task

from constants import CREATE_WAREHOUSE_DB
from data_gen import (UserGen, PurchaseGen, MerchantGen,
                      InstallmentGen)

from logger import logger


@dag
def run_data_platform():
    @task.sql(
        conn_id="warehouse_conn"
    )
    def init_db():
        logger.info("Create or replace warehouse database")
        return CREATE_WAREHOUSE_DB

    @task
    def generate_data():
        logger.info("Generating merchant data")

        merch_gen = MerchantGen()
        merch_df = merch_gen.generate()

        logger.info(f"Generated {merch_df.height} rows of merchant data. Sending to DB...")

        merch_gen.send_to_db(merch_df)

        logger.info("Generating user data...")

        user_gen = UserGen()
        user_df = user_gen.generate()

        logger.info(f"Generated {user_df.height} rows of user data. Sending to DB...")

        user_gen.send_to_db(user_df)

        logger.info("Generating purchase data")

        purch_gen = PurchaseGen(user_df["user_id"].to_list())
        purch_df = purch_gen.generate()

        logger.info(f"Generated {purch_df.height} rows of purchase data. Sending to DB...")

        purch_gen.send_to_db(purch_df)

        logger.info("Generating installment data")

        purch_ids = purch_gen.get_latest_n_ids(5)

        instlmt_gen = InstallmentGen(purch_ids)
        instlmt_df = instlmt_gen.generate()

        logger.info(f"Generated {instlmt_df.height} rows of installment data. Sending to DB...")

        instlmt_gen.send_to_db(instlmt_df)

        return {"status": "success"}

    init_db_task = init_db()
    generate_data_task = generate_data()
    
    init_db_task >> generate_data_task

run_data_platform()
