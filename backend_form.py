from flask import Flask, request, redirect
import pymysql
from datetime import datetime
import json
import urllib.parse

app = Flask(__name__)

@app.route("/submit", methods=["POST"])
def submit():
    conn = pymysql.connect(
        host="localhost",
        user="admin",
        password="Snapegaming193",
        database="army_requisitons",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()

    try:
        reg = request.form.get("reg_number", "").strip()
        serial = request.form.get("weapon_serial", "").strip()

        if not reg or not serial:
            raise ValueError("Both regimental number and weapon serial required")

        # 1. Check soldier exists
        cur.execute("SELECT rank, last_name FROM Soldier WHERE reg_number = %s", (reg,))
        soldier = cur.fetchone()
        if not soldier:
            raise ValueError(f"Soldier {reg} not found")

        rank = soldier['rank']
        lastname = soldier['last_name']

        # 2. Check weapon exists + status
        cur.execute(
            "SELECT weapon_type, Availability FROM Equipment WHERE weapon_serial = %s",
            (serial,)
        )
        weapon = cur.fetchone()
        if not weapon:
            raise ValueError(f"Weapon {serial} not found")

        if weapon['Availability'] != 'Available':
            raise ValueError(f"Weapon {serial} is {weapon['Availability']}")

        # 3. Record issue + update status
        now = datetime.now()
        cur.execute(
            "INSERT INTO Log (reg_number, weapon_serial, issue_date) VALUES (%s, %s, %s)",
            (reg, serial, now)
        )
        cur.execute(
            "UPDATE Equipment SET Availability = 'In Use' WHERE weapon_serial = %s",
            (serial,)
        )

        conn.commit()

        wtype = weapon['weapon_type'] or "Weapon"
        message = f"{wtype} {serial} issued to {reg} {rank} {lastname}"

        # ───────────────────────────────────────────────────────────────
        #  Changed: send the actual data so results.html can display it
        # ───────────────────────────────────────────────────────────────
        result = {
            "message": message,
            "success": True,
            "reg_number": reg,
            "rank": rank,
            "last_name": lastname,
            "weapon_serial": serial
        }

    except Exception as e:
        conn.rollback()
        result = {"message": str(e), "success": False}

    finally:
        cur.close()
        conn.close()

    # Redirect to results
    data = urllib.parse.quote(json.dumps(result))
    return redirect(f"/results.html?data={data}")

if __name__ == "__main__":
    app.run(debug=True)