import sqlite3

conn = sqlite3.connect(
    "approval.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS approvals(
id INTEGER PRIMARY KEY AUTOINCREMENT,
project_name TEXT,
risk_score TEXT,
status TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()