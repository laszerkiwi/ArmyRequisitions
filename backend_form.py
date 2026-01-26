from flask import Flask, request, redirect
import pymysql
import json
import urllib.parse

app = Flask(__name__)

@app.route("/submit", methods=["POST"])
def submit():
    # Connect to local MySQL
    conn = pymysql.connect(
        host="localhost",
        user="admin",
        password="Snapegaming193",
        db="tyre_wear_db"
    )
    cursor = conn.cursor()

    # Read form data safely
    reg_number = request.form.get("reg_number", "")
    rank = request.form.get("rank", "")
    first_name = request.form.get("first_name", "")
    last_name = request.form.get("last_name", "")
    unit = request.form.get("unit", "")
    weapon_serial = request.form.get("weapon_serial", "")

    # INSERT DATA
    cursor.execute(
        """
        INSERT INTO soldier (reg_number, rank, first_name, last_name, unit)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (reg_number, rank, first_name, last_name, unit)
    )

    cursor.execute(
        "INSERT INTO equipment (weapon_serial) VALUES (%s)",
        (weapon_serial,)
    )

    cursor.execute(
        "INSERT INTO log (reg_number, weapon_serial) VALUES (%s, %s)",
        (reg_number, weapon_serial)
    )

    conn.commit()
    cursor.close()
    conn.close()

    # Prepare results
    results = {
        "message": "Record successfully added",
        "reg_number": reg_number,
        "rank": rank,
        "last_name": last_name,
        "weapon_serial": weapon_serial
    }

    encoded_data = urllib.parse.quote(json.dumps(results))

    # Redirect to local HTML file
    return redirect(f"/results.html?data={encoded_data}", code=302)

if __name__ == "__main__":
    app.run(debug=True)