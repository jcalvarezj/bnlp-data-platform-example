import random
from datetime import datetime
from abc import ABC, abstractmethod

import polars as pl
import faker_commerce
from faker import Faker
from polars import DataFrame

from logger import logger
from constants import db_conn_str


class DataGen(ABC):
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    @property
    @abstractmethod
    def table_name(self): ...

    @abstractmethod
    def generate(self) -> DataFrame: ...

    def send_to_db(self, df: DataFrame):
        try:
            df.write_database(
                table_name=self.table_name,
                connection=db_conn_str,
                engine="adbc"
            )
        except Exception as e:
            logger.exception(e)


class UserGen(DataGen):
    num_users = 5
    table_name = "users"

    def generate(self) -> DataFrame:
        users_list = []

        for user_id in range(1, self.num_users + 1):
            name = self.fake.name()
            email = name.lower().replace(" ", "") + "@email.com"
            now = datetime.now()
            users_list.append({
                "user_id": user_id,
                "full_name": name,
                "address": self.fake.address(),
                "city": self.fake.city(),
                "state": self.fake.state(),
                "country": "USA",
                "email": email,
                "credit_limit": round(random.uniform(1000.0, 20000.0), 2),
                "risk_score": random.randint(300, 850),
                "created_at": now,
                "updated_at": now
            })

        return pl.DataFrame(users_list)


class PurchaseGen(DataGen):
    num_purchases = 10
    table_name = "purchases"

    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.fake.add_provider(faker_commerce.Provider)

    def generate(self) -> DataFrame:
        purchases_list = []
        for purchase_id in range(100, 100 + self.num_purchases):
            assigned_user_id = random.choice(self.user_ids)

            purchases_list.append({
                "purchase_id": purchase_id,
                "user_id": assigned_user_id,
                "product": self.fake.bs().title(),
                "price": round(random.uniform(10.0, 500.0), 2),
                "purchase_date": self.fake.date_this_year().strftime("%Y-%m-%d")
            })

        return pl.DataFrame(purchases_list)


if __name__ == "__main__":
    ug = UserGen()
    users_df = ug.generate()
    user_ids = users_df["user_id"].to_list()

    pg = PurchaseGen(user_ids)
    purchases_df = pg.generate()

    ug.send_to_db(users_df)
    pg.send_to_db(purchases_df)

    print("OK")
