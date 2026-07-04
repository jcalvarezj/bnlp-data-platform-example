from airflow.sdk import dag, task

from data_gen import UserGen, PurchaseGen


@dag
def run_data_platform():
    @task
    def generate_data():
        logger.info("Generating user data...")

        user_gen = UserGen()
        user_df = user_gen.generate()

        logger.info(f"Generated {user_df.height} rows of user data. Sending to DB...")

        user_gen.send_to_db(user_df)

        logger.info("Generating purchase data")

        purch_gen = PurchaseGen(user_df["user_id"].to_list())
        purch_df = purch_gen.generate()

        return {"status": "success"}

    generate_data_task = generate_data()

    generate_data_task

run_data_platform()
