from config.db_config import db_connection


def fetch_all(query, params=None):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            columns = [column[0].lower() for column in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def fetch_one(query, params=None):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            row = cursor.fetchone()

            if row is None:
                return None

            columns = [column[0].lower() for column in cursor.description]
            return dict(zip(columns, row))


def execute(query, params=None):
    with db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
                affected_rows = cursor.rowcount

            connection.commit()
            return affected_rows
        except Exception:
            connection.rollback()
            raise


def execute_many(query, params_list):
    with db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                affected_rows = cursor.rowcount

            connection.commit()
            return affected_rows
        except Exception:
            connection.rollback()
            raise
