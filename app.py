# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import (
    init_app_schema,
    get_connections_for_user,
    get_connection_by_id,
    get_primary_connection_for_user,
    set_primary_connection,
    update_connection,
    delete_connection,
)
from auth import create_user, verify_user, login_required, current_user_id
from db import execute_non_query
from nlp_rules import parse_query as parse_rules, extract_params
from nlp_groq import nl_to_sql_with_groq
from user_db import UserDBConfig, execute_user_query, get_user_db_schema

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        init_app_schema()

    # ---------------------- Auth ---------------------------------------

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not email or not password:
                flash("Email and password are required.", "error")
                return redirect(url_for("register"))
            try:
                create_user(email, password)
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Registration failed: {e}", "error")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user_id = verify_user(email, password)
            if user_id:
                session["user_id"] = user_id
                flash("Logged in successfully.", "success")
                next_url = request.args.get("next") or url_for("index")
                return redirect(next_url)
            else:
                flash("Invalid email or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "info")
        return redirect(url_for("login"))

    # ---------------------- Connections --------------------------------

    @app.route("/connections", methods=["GET", "POST"])
    @login_required
    def connections():
        user_id = current_user_id()

        # Handle new connection creation
        if request.method == "POST" and request.form.get("action") == "create":
            name = request.form.get("name", "").strip()
            host = request.form.get("host", "").strip()
            port = int(request.form.get("port", "3306"))
            db_name = request.form.get("db_name", "").strip()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not all([name, host, db_name, username, password]):
                flash("All fields are required.", "error")
                return redirect(url_for("connections"))

            execute_non_query(
                "INSERT INTO db_connections "
                "(user_id, name, db_type, host, port, db_name, username, password_plain, is_primary) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0);",
                (user_id, name, "mysql", host, port, db_name, username, password),
            )
            flash("Connection added.", "success")
            return redirect(url_for("connections"))

        conns = get_connections_for_user(user_id)
        return render_template("connections.html", connections=conns)

    @app.route("/connections/set_primary/<int:conn_id>", methods=["POST"])
    @login_required
    def set_primary(conn_id):
        user_id = current_user_id()
        conn = get_connection_by_id(user_id, conn_id)
        if not conn:
            flash("Connection not found.", "error")
            return redirect(url_for("connections"))
        set_primary_connection(user_id, conn_id)
        flash("Primary connection updated.", "success")
        return redirect(url_for("connections"))

    @app.route("/connections/edit/<int:conn_id>", methods=["POST"])
    @login_required
    def edit_connection(conn_id):
        user_id = current_user_id()
        conn = get_connection_by_id(user_id, conn_id)
        if not conn:
            flash("Connection not found.", "error")
            return redirect(url_for("connections"))

        name = request.form.get("name", "").strip()
        host = request.form.get("host", "").strip()
        port = int(request.form.get("port", conn["port"]))
        db_name = request.form.get("db_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip() or conn["password_plain"]

        if not all([name, host, db_name, username]):
            flash("Name, host, database, and username are required.", "error")
            return redirect(url_for("connections"))

        update_connection(user_id, conn_id, name, host, port, db_name, username, password)
        flash("Connection updated.", "success")
        return redirect(url_for("connections"))

    @app.route("/connections/delete/<int:conn_id>", methods=["POST"])
    @login_required
    def delete_connection_route(conn_id):
        user_id = current_user_id()
        conn = get_connection_by_id(user_id, conn_id)
        if not conn:
            flash("Connection not found.", "error")
            return redirect(url_for("connections"))

        delete_connection(user_id, conn_id)
        flash("Connection deleted.", "success")
        return redirect(url_for("connections"))

    # ---------------------- Query page ----------------------------------

    @app.route("/", methods=["GET", "POST"])
    @login_required
    def index():
        user_id = current_user_id()
        conn_row = get_primary_connection_for_user(user_id)
        if not conn_row:
            flash("Please add and set a primary database connection first.", "info")
            return redirect(url_for("connections"))

        cfg = UserDBConfig(conn_row)

        context = {
            "nl_query": "",
            "sql": None,
            "rows": None,
            "columns": None,
            "error": None,
            "connection_name": cfg.name,
        }

        if request.method == "POST":
            nl_query = request.form.get("query", "")
            context["nl_query"] = nl_query

            sql, error = parse_rules(nl_query)
            params = ()
            if sql is not None:
                params = extract_params(nl_query)

            # Fallback to Groq if rules did not match
            if sql is None and error == "pattern_not_matched":
                schema_str = get_user_db_schema(cfg)
                sql, error = nl_to_sql_with_groq(
                    question=nl_query,
                    schema_description=schema_str,
                    db_type="MySQL",
                )

            if error:
                context["error"] = error
                return render_template("index.html", **context)

            try:
                rows = execute_user_query(cfg, sql, params)
                context["sql"] = sql
                context["rows"] = rows
                context["columns"] = list(rows[0].keys()) if rows else []
            except RuntimeError as e:
                context["error"] = str(e)

        return render_template("index.html", **context)

    return app