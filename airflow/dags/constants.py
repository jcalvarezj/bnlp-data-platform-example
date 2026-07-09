import os
from datetime import datetime

from polars import DataFrame
from dotenv import load_dotenv


load_dotenv()

STATUS_PENDING = "PENDING"

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_CONN_STR = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

CREATE_WAREHOUSE_DB = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '{DB_NAME}') THEN
            CREATE DATABASE {DB_NAME};
        END IF;
    END $$;
"""

GET_LATEST_ID_FROM = """
    SELECT MAX({prefix}_id) FROM {table}
"""

GET_LATEST_N_IDS_FROM = """
    SELECT {prefix}_id FROM {table}
     ORDER BY created_at
     LIMIT {n}
"""
