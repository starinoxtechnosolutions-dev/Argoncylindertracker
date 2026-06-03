import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime

DB = "cylinders.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT * FROM cylinders ORDER BY id DESC")
rows = cur.fetchall()
conn.close()

columns = [
    "ID",
    "Cylinder No",
    "Site",
    "Taken By",
    "Date Out",
    "Date Returned",
    "Status"
]

df = pd.DataFrame(rows, columns=columns)

# Convert date_out safely
def check_overdue(row):
    if row["Status"] != "OUT":
        return "OK"

    try:
        date_out = datetime.strptime(row["Date Out"], "%d-%m-%Y %H:%M")
        days = (datetime.now() - date_out).days

        if days > 10:
            return "OVERDUE"
        else:
            return "OK"
    except:
        return "UNKNOWN"

df["Alert"] = df.apply(check_overdue, axis=1)

st.subheader("Current Cylinders")

st.dataframe(df, use_container_width=True)