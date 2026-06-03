from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "cylinders.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cylinders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cylinder_no TEXT UNIQUE,
        site TEXT,
        taken_by TEXT,
        date_out TEXT,
        date_returned TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Argon Cylinder Tracker</title>
    <style>
        body{
            font-family:Arial;
            margin:40px;
            background:#f4f4f4;
        }

        .container{
            background:white;
            padding:20px;
            border-radius:10px;
        }

        input,button{
            padding:10px;
            margin:5px;
        }

        table{
            width:100%;
            border-collapse:collapse;
            margin-top:20px;
        }

        th,td{
            border:1px solid #ddd;
            padding:10px;
            text-align:center;
        }

        th{
            background:#333;
            color:white;
        }

        .out{
            color:red;
            font-weight:bold;
        }

        .returned{
            color:green;
            font-weight:bold;
        }
    </style>
</head>
<body>

<div class="container">

<h2>Argon Cylinder Tracking System</h2>

<form action="/issue" method="POST">
    <input type="text" name="cylinder_no" placeholder="Cylinder Number" required>
    <input type="text" name="site" placeholder="Site Name" required>
    <input type="text" name="taken_by" placeholder="Taken By" required>

    <button type="submit">Issue Cylinder</button>
</form>

<h3>Current Cylinders</h3>

<table>
<tr>
<th>ID</th>
<th>Cylinder No</th>
<th>Site</th>
<th>Taken By</th>
<th>Date Out</th>
<th>Date Returned</th>
<th>Status</th>
<th>Action</th>
</tr>

{% for row in cylinders %}
<tr>
<td>{{row[0]}}</td>
<td>{{row[1]}}</td>
<td>{{row[2]}}</td>
<td>{{row[3]}}</td>
<td>{{row[4]}}</td>
<td>{{row[5] if row[5] else "-"}}</td>

<td>
{% if row[6] == 'OUT' %}
<span class="out">OUT</span>
{% else %}
<span class="returned">RETURNED</span>
{% endif %}
</td>

<td>
{% if row[6] == 'OUT' %}
<a href="/return/{{row[0]}}">
<button>Return</button>
</a>
{% else %}
-
{% endif %}
</td>
</tr>
{% endfor %}
</table>

</div>

</body>
</html>
"""

@app.route("/")
def home():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM cylinders ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return render_template_string(HTML, cylinders=data)

@app.route("/issue", methods=["POST"])
def issue():
    cylinder_no = request.form["cylinder_no"]
    site = request.form["site"]
    taken_by = request.form["taken_by"]

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO cylinders
    (cylinder_no, site, taken_by, date_out, status)
    VALUES (?, ?, ?, ?, ?)
    """, (
        cylinder_no,
        site,
        taken_by,
        datetime.now().strftime("%d-%m-%Y %H:%M"),
        "OUT"
    ))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/return/<int:id>")
def return_cylinder(id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE cylinders
    SET status=?,
        date_returned=?
    WHERE id=?
    """, (
        "RETURNED",
        datetime.now().strftime("%d-%m-%Y %H:%M"),
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/")

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )