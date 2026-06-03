import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB = "cylinders.db"

# ---------------- DATABASE INIT ----------------
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

# ---------------- UI ----------------
st.title("🟢 Argon Cylinder Tracker")

# ---------------- ISSUE CYLINDER ----------------
st.subheader("Issue Cylinder")

with st.form("issue_form"):
    cylinder_no = st.text_input("Cylinder Number")
    site = st.text_input("Site Name")
    taken_by = st.text_input("Taken By")
    submit = st.form_submit_button("Issue Cylinder")

if submit:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO cylinders (cylinder_no, site, taken_by, date_out, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            cylinder_no,
            site,
            taken_by,
            datetime.now().strftime("%d-%m-%Y %H:%M"),
            "OUT"
        ))

        conn.commit()
        st.success("Cylinder Issued!")

    except Exception as e:
        st.error(f"Error: {e}")

    conn.close()

# ---------------- LOAD DATA ----------------
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

# ---------------- OVERDUE LOGIC ----------------
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

# ---------------- RETURN CYLINDER ----------------
st.subheader("Return Cylinder")

return_id = st.number_input("Enter Cylinder ID to return", min_value=1, step=1)

if st.button("Mark as Returned"):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    UPDATE cylinders
    SET status='RETURNED',
        date_returned=?
    WHERE id=?
    """, (datetime.now().strftime("%d-%m-%Y %H:%M"), return_id))

    conn.commit()
    conn.close()

    st.success("Cylinder marked as RETURNED")
    st.rerun()

# ---------------- TABLE DISPLAY ----------------
st.subheader("Current Cylinders")

def style_alert(row):
    if row["Alert"] == "OVERDUE":
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)

st.dataframe(df, use_container_width=True)

# ---------------- OVERDUE SECTION ----------------
st.subheader("⚠ Overdue Cylinders (>10 days)")

overdue_df = df[df["Alert"] == "OVERDUE"]

st.dataframe(overdue_df, use_container_width=True)