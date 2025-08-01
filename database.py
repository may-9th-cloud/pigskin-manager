import psycopg2
import pandas as pd
import os

# PostgreSQL 連線參數
DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# 建立連線
def get_connection():
    return psycopg2.connect(**DB_PARAMS)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pigskin (
            id SERIAL PRIMARY KEY,
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
    conn = get_connection()
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
    conn = get_connection()
    c = conn.cursor()
    full_packages = packages - 1 if note else packages
    for _ in range(full_packages):
        c.execute("""
            INSERT INTO pigskin (date, source, breed, reason, drug, pieces, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (date, source, breed, reason, drug, 6, ""))
    if note:
        c.execute("""
            INSERT INTO pigskin (date, source, breed, reason, drug, pieces, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (date, source, breed, reason, drug, pieces, note))
    conn.commit()
    conn.close()

def get_total_pieces():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(pieces) FROM pigskin WHERE used=0")
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0

def get_all_records_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pigskin", conn)
    conn.close()
    return df

def get_unused_packages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, date, pieces, note FROM pigskin WHERE used=0")
    data = c.fetchall()
    conn.close()
    return data

def use_package(id, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE pigskin SET used=1, used_date=%s WHERE id=%s", (date, id))
    conn.commit()
    conn.close()

def get_usage_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pigskin WHERE used=1", conn)
    conn.close()
    return df
