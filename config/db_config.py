import os
from contextlib import contextmanager

import oracledb


DB_USER = os.getenv("DB_USER", "wildguard")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wildguard123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME", "XE")

ORACLE_CLIENT_DIR = os.getenv(
    "ORACLE_CLIENT_DIR",
    r"C:\oraclexe\instantclient_19_25"
)


def init_oracle_client():
    try:
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)
    except oracledb.ProgrammingError:
        # 이미 초기화된 경우 무시
        pass


def get_dsn() -> str:
    return oracledb.makedsn(
        host=DB_HOST,
        port=DB_PORT,
        service_name=DB_SERVICE_NAME,
    )


def get_connection() -> oracledb.Connection:
    init_oracle_client()

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