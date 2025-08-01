import sqlite3
import os
import pandas as pd
DB_NAME = os.path.join(os.path.dirname(__file__), "pigskin.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pigskin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            source TEXT,
            breed TEXT,
            reason TEXT,
            drug TEXT,
            pieces INTEGER,
            note TEXT,
            used INTEGER DEFAULT 0,
            used_date TEXT
        )
    """)
    conn.commit()
    conn.close()
    
def get_available_packages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, date, source, pieces, note FROM pigskin
        WHERE used = 0
    ''')
    rows = c.fetchall()
    conn.close()
    packages = [
        {
            "id": r[0],
            "date": r[1],
            "source": r[2],
            "pieces": r[3],
            "note": r[4]
        } for r in rows
    ]
    return packages


def insert_pigskin_record(date, source, breed, reason, drug, packages, pieces, note):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 每包都插入一筆資料（實際片數為 6，除非最後一包有特別片數）
    full_packages = packages - 1 if note else packages
    for _ in range(full_packages):
        c.execute("INSERT INTO pigskin (date, source, breed, reason, drug, pieces, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (date, source, breed, reason, drug, 6, ""))
    if note:  # 插入不足6片的那一包
        c.execute("INSERT INTO pigskin (date, source, breed, reason, drug, pieces, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (date, source, breed, reason, drug, pieces, note))
    conn.commit()
    conn.close()

def get_total_pieces():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT SUM(pieces) FROM pigskin WHERE used=0")
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0

import pandas as pd

def get_all_records_df():
    conn = sqlite3.connect(DB_NAME)
    all_df = pd.read_sql_query("SELECT * FROM pigskin", conn)
    conn.close()
    return all_df


def get_unused_packages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, date, pieces, note FROM pigskin WHERE used=0")
    data = c.fetchall()
    conn.close()
    return data

def use_package(id, date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE pigskin SET used=1, used_date=? WHERE id=?", (date, id))
    conn.commit()
    conn.close()

def get_usage_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM pigskin WHERE used=1", conn)
    conn.close()
    return df

