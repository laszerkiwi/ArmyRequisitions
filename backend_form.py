import pymysql
import json
import urllib.parse

def lambda_handler(event, context):
    # Connect to the MySQL database
    conn = pymysql.connect(
        host='',
        user='admin',
        password='Snapegaming193',
        db='tyre_wear_db'
    )
    cursor = conn.cursor()

    # Parse form data from body (x-www-form-urlencoded)
    body = event.get('body', '')
    form_data = dict(x.split('=') for x in body.split('&'))

    # Extract fields
    reg_number = form_data.get('reg_number', '0')
    rank = form_data.get('rank', '0')
    first_name = form_data.get('first_name', '0')
    last_name = form_data.get('last_name', '0')
    unit = form_data.get('unit', '0')
    weapon_serial = form_data.get('weapon_serial', '0')

    # Query tyre data
    cursor.execute('SELECT base_wear FROM tyre WHERE tyre_name = %s', (tyre_name,))
    result = cursor.fetchone()

    if result:
        # Insert into DB
        cursor.execute(
            'INSERT INTO soldier (reg_number, rank, first_name, last_name, unit) VALUES (%s, %s, %s, %s, %s)',
            (reg_number, rank, first_name, last_name, unit)
        )
        cursor.execute(
            'INSERT INTO log (reg_number, weapon_serial) VALUES (%s, %s)',
            (reg_number, weapon_serial)
        )
        cursor.execute(
            'INSERT INTO equipment (weapon_serial) VALUES (%s)',
            (weapon_serial,)
        )

        conn.commit()

    # Close DB connection
    cursor.close()
    conn.close()

    # Prepare results
    results = {
        "reg_number": reg_number,
        "rank": rank,
        "last_name": last_name,
        "weapon_serial": weapon_serial,
    }

    # Encode results into query string
    encoded_data = urllib.parse.quote(json.dumps(results))

    # Redirect user to results page
    return {
        "statusCode": 302,
        "headers": {
            "Location": f"https://tyre-wear-calculator.s3-website-ap-southeast-2.amazonaws.com/results.html?data={encoded_data}",
            "Access-Control-Allow-Origin": "*"
        },
        "body": ""
    }