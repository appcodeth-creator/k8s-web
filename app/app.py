import os
import time
from flask import Flask, render_template_string
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "Web")
DB_HOST = os.getenv("DB_HOST", "mysql-service")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cloud123")
DB_NAME = os.getenv("DB_NAME", "appdb")

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ app_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        table { border-collapse: collapse; width: 100%; max-width: 900px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <h1>{{ app_name }}</h1>
    <p>Connected to MySQL through <strong>mysql-service</strong></p>
    <table>
        <tr><th>ID</th><th>App</th><th>Message</th><th>Created At</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def connect_db(retries=30):
    # Retry because MySQL may need time to become ready.
    for attempt in range(retries):
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        except Error:
            if attempt == retries - 1:
                raise
            time.sleep(2)

@app.route("/")
def index():
    conn = connect_db()
    cursor = conn.cursor()

    # Create the table automatically for this classroom workshop.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            app_name VARCHAR(50) NOT NULL,
            message VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(
        "INSERT INTO visitors (app_name, message) VALUES (%s, %s)",
        (APP_NAME, f"Hello from {APP_NAME}")
    )
    conn.commit()

    cursor.execute("""
        SELECT id, app_name, message, created_at
        FROM visitors
        ORDER BY id DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template_string(HTML, app_name=APP_NAME, rows=rows)

@app.route("/health")
def health():
    return {"status": "ok", "app": APP_NAME}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
