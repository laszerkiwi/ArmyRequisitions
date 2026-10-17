# Army Requisitions

## Run locally

From the project folder, create and activate a virtual environment, then install
the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install Flask PyMySQL
```

Set the connection details for your existing MySQL database in PowerShell
(replace the example values with your local settings):

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_USER = "admin"
$env:DB_PASSWORD = "your-local-password"
$env:DB_NAME = "army_requisitons"
```

Start the Flask app and open the local address:

```powershell
python backend_form.py
```

Visit <http://127.0.0.1:5000/>. The database must already contain the
`Soldier`, `Equipment`, and `Log` tables expected by the app.
