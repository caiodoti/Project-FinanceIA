import sqlite3

def get_db():
    conn = sqlite3.connect('finance.db')
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        pin TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        amount REAL,
        category TEXT,
        description TEXT,
        date TEXT
    )''')
    conn.commit()
    conn.close()
