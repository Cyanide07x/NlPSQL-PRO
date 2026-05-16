# models.py
from db import execute_non_query, execute_query

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS db_connections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    db_type VARCHAR(20) NOT NULL,
    host VARCHAR(255),
    port INT,
    db_name VARCHAR(255),
    username VARCHAR(255),
    password_plain VARCHAR(255),
    is_primary TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

def init_app_schema():
    for stmt in SCHEMA_SQL.strip().split(";"):
        sql = stmt.strip()
        if sql:
            execute_non_query(sql + ";")


# ---- Users -------------------------------------------------------------

def get_user_by_email(email: str):
    rows = execute_query("SELECT * FROM users WHERE email = %s;", (email,))
    return rows[0] if rows else None

def get_user_by_id(user_id: int):
    rows = execute_query("SELECT * FROM users WHERE id = %s;", (user_id,))
    return rows[0] if rows else None


# ---- DB connections ----------------------------------------------------

def get_connections_for_user(user_id: int):
    return execute_query(
        "SELECT * FROM db_connections WHERE user_id = %s ORDER BY created_at DESC;",
        (user_id,),
    )

def get_connection_by_id(user_id: int, conn_id: int):
    rows = execute_query(
        "SELECT * FROM db_connections WHERE user_id = %s AND id = %s;",
        (user_id, conn_id),
    )
    return rows[0] if rows else None

def get_primary_connection_for_user(user_id: int):
    rows = execute_query(
        "SELECT * FROM db_connections WHERE user_id = %s AND is_primary = 1 LIMIT 1;",
        (user_id,),
    )
    return rows[0] if rows else None

def set_primary_connection(user_id: int, conn_id: int):
    execute_non_query(
        "UPDATE db_connections SET is_primary = 0 WHERE user_id = %s;",
        (user_id,),
    )
    execute_non_query(
        "UPDATE db_connections SET is_primary = 1 WHERE user_id = %s AND id = %s;",
        (user_id, conn_id),
    )

def update_connection(user_id: int, conn_id: int, name, host, port, db_name, username, password):
    execute_non_query(
        "UPDATE db_connections "
        "SET name=%s, host=%s, port=%s, db_name=%s, username=%s, password_plain=%s "
        "WHERE id=%s AND user_id=%s;",
        (name, host, port, db_name, username, password, conn_id, user_id),
    )

def delete_connection(user_id: int, conn_id: int):
    execute_non_query(
        "DELETE FROM db_connections WHERE id=%s AND user_id=%s;",
        (conn_id, user_id),
    )