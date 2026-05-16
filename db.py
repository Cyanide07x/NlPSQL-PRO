# db.py
import threading
import mysql.connector
from mysql.connector import Error
from config import Config

_connection_local = threading.local()

def get_app_connection():
    conn = getattr(_connection_local, "app_conn", None)
    if conn is None or not conn.is_connected():
        conn = mysql.connector.connect(
            host=Config.APP_DB_HOST,
            port=Config.APP_DB_PORT,
            user=Config.APP_DB_USER,
            password=Config.APP_DB_PASSWORD,
            database=Config.APP_DB_NAME,
        )
        _connection_local.app_conn = conn
    return conn

def execute_query(sql, params=None):
    conn = get_app_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    except Error as e:
        raise RuntimeError(f"App DB error: {e}") from e

def execute_non_query(sql, params=None):
    conn = get_app_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
    except Error as e:
        conn.rollback()
        raise RuntimeError(f"App DB error: {e}") from e