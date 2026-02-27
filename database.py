import sqlite3
from datetime import datetime

DB_NAME = "analysis.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            query TEXT,
            answer TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_log(file_name, query, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_logs (file_name, query, answer, created_at)
        VALUES (?, ?, ?, ?)
    """, (file_name, query, answer, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()