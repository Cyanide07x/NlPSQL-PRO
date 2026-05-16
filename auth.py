# auth.py
from functools import wraps
from flask import session, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_non_query, execute_query

def create_user(email: str, password: str):
    pwd_hash = generate_password_hash(password)
    execute_non_query(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s);",
        (email, pwd_hash),
    )

def verify_user(email: str, password: str):
    rows = execute_query(
        "SELECT id, password_hash FROM users WHERE email = %s;",
        (email,),
    )
    if not rows:
        return None
    user = rows[0]
    if check_password_hash(user["password_hash"], password):
        return user["id"]
    return None

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapper

def current_user_id():
    return session.get("user_id")