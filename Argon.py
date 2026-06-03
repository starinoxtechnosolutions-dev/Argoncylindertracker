import streamlit as st
import sqlite3
from datetime import datetime

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

st.title("Argon Cylinder Tracker")

# Issue form
with st.form("issue_form"):
    cylinder_no = st.text_input("Cylinder Number")
    site = st.text_input("Site Name")
    taken_by = st.text_input("Taken By")
    submit = st.form_submit_button("Issue Cylinder")

if submit:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO cylinders (cylinder_no, site, taken_by, date_out, status)
    VALUES (?, ?, ?, ?, ?)
    """, (cylinder_no, site, taken_by,
          datetime.now().strftime("%d-%m-%Y %H:%M"),
          "OUT"))
    conn.commit()
    conn.close()
    st.success("Cylinder Issued!")

# Display data
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT * FROM cylinders ORDER BY id DESC")
rows = cur.fetchall()
conn.close()

st.subheader("Current Cylinders")

for r in rows:
    st.write(r)
    if r[6] == "OUT":
        if st.button(f"Return {r[0]}"):
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("""
            UPDATE cylinders
            SET status='RETURNED',
                date_returned=?
            WHERE id=?
            """, (datetime.now().strftime("%d-%m-%Y %H:%M"), r[0]))
            conn.commit()
            conn.close()
            st.rerun()