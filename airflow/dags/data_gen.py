import random
from datetime import datetime
from abc import ABC, abstractmethod

import polars as pl
import faker_commerce
from faker import Faker
from polars import DataFrame
from adbc_driver_manager import ProgrammingError

from logger import logger
from constants import (DB_CONN_STR, GET_LATEST_ID_FROM, STATUS_PENDING,
                       GET_LATEST_N_IDS_FROM)


class DataGen(ABC):
    fake = Faker()
    table_write_mode = "append"

    @property
    @abstractmethod
    def table_name(self): ...

    @property
    @abstractmethod
    def table_prefix(self): ...

    @abstractmethod
    def generate(self) -> DataFrame: ...

    def get_latest_id(self) -> int:
        try:
            return pl.read_database_uri(
                GET_LATEST_ID_FROM.replace("{prefix}", self.table_prefix) \
                    .replace("{table}", self.table_name),
                DB_CONN_STR, engine="adbc"
            )["max"][0]
        except ProgrammingError as e:
            if "NOT_FOUND" in str(e):
                return 0
            else:
                logger.exception(e)
                raise e

    def get_latest_n_ids(self, n: int) -> int:
        try:
            return pl.read_database_uri(
                GET_LATEST_N_IDS_FROM.replace("{prefix}", self.table_prefix) \
                    .replace("{table}", self.table_name).replace("{n}", f"{n}"),
                DB_CONN_STR, engine="adbc"
            )[f"{self.table_prefix}_id"].to_list()
        except ProgrammingError as e:
            if "NOT_FOUND" in str(e):
                return 0
            else:
                logger.exception(e)
                raise e

    def send_to_db(self, df: DataFrame):
        try:
            df.write_database(
                table_name=self.table_name,
                if_table_exists=self.table_write_mode,
                connection=DB_CONN_STR,
                engine="adbc"
            )
        except Exception as e:
            logger.exception(f"An error occurred when sending data to the database: {e}")
            raise e


class MerchantGen(DataGen):
    num_merchs = 5
    table_name = "merchants"
    table_prefix = "merchant"
    table_write_mode = "replace"

    def generate(self) -> DataFrame:
        merchs_list = []

        for merch_id in range(1, self.num_merchs):
            now = datetime.now()
            merchs_list.append({
                "merchant_id": merch_id,
                "id_number": self.fake.numerify("9####-####"),
                "name": self.fake.bs().capitalize(),
                "address": self.fake.address(),
                "created_at": now,
                "updated_at": now
            })

        return DataFrame(merchs_list)


class UserGen(DataGen):
    num_users = 5
    table_name = "users"
    table_prefix = "user"

    def generate(self) -> DataFrame:
        users_list = []
        latest_id = self.get_latest_id()

        for user_id in range(1 + latest_id, self.num_users + 1 + latest_id):
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
    table_prefix = "purchase"

    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.fake.add_provider(faker_commerce.Provider)

    def generate(self) -> DataFrame:
        purchases_list = []
        latest_id = self.get_latest_id()
        now = datetime.now()

        for purchase_id in range(100 + latest_id, 100 + self.num_purchases + latest_id):
            assigned_user_id = random.choice(self.user_ids)

            purchases_list.append({
                "purchase_id": purchase_id,
                "merchant_id": random.randint(1, 3),
                "user_id": assigned_user_id,
                "product_id": self.fake.numerify("@@-#####"),
                "product_name": self.fake.bs().title(),
                "purchase_value": round(random.uniform(10.0, 500.0), 2),
                "purchase_date": self.fake.date_this_year().strftime("%Y-%m-%d"),
                "created_at": now,
                "updated_at": now
            })

        return pl.DataFrame(purchases_list)


class InstallmentGen(DataGen):
    num_instlmt_per_purchase = 3
    table_name = "installments"
    table_prefix = "installment"
    table_write_mode = "replace"

    def __init__(self, purchases_list):
        self.purchases_list = purchases_list

    def generate(self):
        installments_list = []
        installment_id = 0
        now = datetime.now()

        for purch_id in self.purchases_list:
            for _ in range(1, self.num_instlmt_per_purchase + 1):
                installment_id += 1
                capital_value = random.uniform(10.0, 20000.0)
                interest_value = capital_value * 0.03
                installments_list.append({
                    "installment_id": installment_id,
                    "purchase_id": purch_id,
                    "due_date": self.fake.date_between("+1y", "+2y"),
                    "capital_value": capital_value,
                    "interest_value": interest_value,
                    "total_value": capital_value + interest_value,
                    "status": STATUS_PENDING,
                    "purchase_id": purch_id,
                    "created_at": now,
                    "updated_at": now
                })

        return DataFrame(installments_list)
