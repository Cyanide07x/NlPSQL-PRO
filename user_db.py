# user_db.py
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, List

class UserDBConfig:
    def __init__(self, row: Dict[str, Any]):
        self.id = row["id"]
        self.user_id = row["user_id"]
        self.name = row["name"]
        self.db_type = row["db_type"]
        self.host = row["host"]
        self.port = row["port"]
        self.db_name = row["db_name"]
        self.username = row["username"]
        self.password = row["password_plain"]

def connect_mysql(cfg: UserDBConfig):
    return mysql.connector.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.username,
        password=cfg.password,
        database=cfg.db_name,
    )

def execute_user_query(cfg: UserDBConfig, sql: str, params=()):
    if cfg.db_type != "mysql":
        raise RuntimeError("Only MySQL user databases are supported in this version.")
    try:
        conn = connect_mysql(cfg)
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        conn.close()
        return rows
    except Error as e:
        raise RuntimeError(f"User DB error: {e}") from e

def get_user_db_schema(cfg: UserDBConfig) -> str:
    conn = connect_mysql(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            tables = [t[0] for t in cur.fetchall()]
            schema_lines: List[str] = []
            for t in tables:
                cur.execute(f"DESCRIBE {t};")
                cols = cur.fetchall()
                col_desc = ", ".join(f"{c[0]} {c[1]}" for c in cols)
                schema_lines.append(f"Table {t}: {col_desc}")
        return "\n".join(schema_lines)
    finally:
        conn.close()