import os
from datetime import datetime
from collections import OrderedDict

from polars import DataFrame
from dotenv import load_dotenv


load_dotenv()

RAW_SCHEMA = "raw"
INTEREST_RATE = 0.03
PAYMENT_METHODS = {
    "CA": "Cash",
    "CC": "Credit Card",
    "BA": "Bank Account"
}
STATUS_TYPES = {
    "PE": "Pending",
    "PA": "Paid",
    "LA": "Late"
}

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
PG_CONN_STR = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
DB_CONN_STR = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
AIRFLOW_DB_CONN = os.getenv("AIRFLOW_DB_CONN")
AIRFLOW_DB_DW_CONN = os.getenv("AIRFLOW_DB_DW_CONN")

GET_WAREHOUSE_DB = f"""
    SELECT FROM pg_database
     WHERE datname = '{DB_NAME}'
"""

CREATE_WAREHOUSE_DB = f"""
    CREATE DATABASE {DB_NAME}
"""

CREATE_RAW_SCHEMA = """
    CREATE SCHEMA IF NOT EXISTS raw;
"""

GET_LATEST_ID_FROM = f"""
    SELECT MAX([prefix]_id) FROM {RAW_SCHEMA}.[table]
"""

GET_LATEST_N_ROWS_FROM = f"""
    SELECT [cols]
      FROM {RAW_SCHEMA}.[table]
  ORDER BY created_at
     LIMIT [n]
"""

GET_PAID_INSTALLMENTS = f"""
    SELECT installment_id, total_value FROM {RAW_SCHEMA}.installments
     WHERE status = 'PA'
"""
