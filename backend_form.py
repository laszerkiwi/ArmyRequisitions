import json
import os
import urllib.parse
from datetime import datetime

import pymysql
from flask import Flask, jsonify, redirect, request, send_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "army_requisitons"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def encode_result(result):
    return urllib.parse.quote(json.dumps(result, ensure_ascii=False))


@app.route("/", methods=["GET"])
def index_page():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/form", methods=["GET"])
def form_page():
    return send_file(os.path.join(BASE_DIR, "signout_form.html"))


@app.route("/signout_form.html", methods=["GET"])
def legacy_form_page():
    return send_file(os.path.join(BASE_DIR, "signout_form.html"))


@app.route("/results.html", methods=["GET"])
def results_page():
    return send_file(os.path.join(BASE_DIR, "results.html"))


@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok"}


@app.route("/submit", methods=["POST"])
def submit():
    conn = None
    cur = None
    result = {"message": "An unexpected error occurred.", "success": False}

    try:
        reg = (request.form.get("reg_number") or "").strip()
        serial = (request.form.get("weapon_serial") or "").strip()

        if not reg or not serial:
            raise ValueError("Both regimental number and weapon serial are required.")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT rank, last_name FROM Soldier WHERE reg_number = %s", (reg,))
        soldier = cur.fetchone()
        if soldier is None:
            raise ValueError(f"Soldier {reg} not found.")

        rank = str(soldier.get("rank") or "").strip()
        lastname = str(soldier.get("last_name") or "").strip()

        cur.execute(
            "SELECT weapon_type, Availability FROM Equipment WHERE weapon_serial = %s",
            (serial,),
        )
        weapon = cur.fetchone()
        if weapon is None:
            raise ValueError(f"Weapon {serial} not found.")

        availability = str(weapon.get("Availability") or "").strip()
        if availability != "Available":
            raise ValueError(f"Weapon {serial} is {availability or 'not available'}.")

        now = datetime.now()
        cur.execute(
            "INSERT INTO Log (reg_number, weapon_serial, issue_date) VALUES (%s, %s, %s)",
            (reg, serial, now),
        )
        cur.execute(
            "UPDATE Equipment SET Availability = 'In Use' WHERE weapon_serial = %s",
            (serial,),
        )

        conn.commit()

        weapon_type = str(weapon.get("weapon_type") or "Weapon").strip() or "Weapon"
        message = f"{weapon_type} {serial} issued to {reg} {rank} {lastname}".strip()

        result = {
            "message": message,
            "success": True,
            "reg_number": reg,
            "rank": rank,
            "last_name": lastname,
            "weapon_serial": serial,
        }

    except Exception as exc:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        result = {"message": str(exc), "success": False}

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    wants_json = (
        request.accept_mimetypes.accept_json
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.args.get("format") == "json"
    )

    if wants_json:
        return jsonify(result), (200 if result.get("success") else 400)

    return redirect(f"/results.html?data={encode_result(result)}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
