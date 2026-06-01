import os
from contextlib import contextmanager

import oracledb


DB_USER = os.getenv("DB_USER", "wildguard")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wildguard123")
DB_HOST = os.getenv("DB_HOST", "192.168.219.103")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME", "XEPDB1")


def get_dsn() -> str:
    return oracledb.makedsn(
        host=DB_HOST,
        port=DB_PORT,
        service_name=DB_SERVICE_NAME,
    )


def get_connection() -> oracledb.Connection:
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=get_dsn(),
    )


@contextmanager
def db_connection():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()