import sqlite3

conn = sqlite3.connect("user.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS clients(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    usluga TEXT,
    day TEXT,
    time TEXT
)
""")
conn.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS slots(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    time TEXT,
    is_free INTEGER DEFAULT 1
)
""")
conn.commit()

def save_zayvka(user_id, name, phone, usluga, day, time):
    cursor.execute(
        "INSERT INTO clients(user_id, name, phone, usluga, day, time) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, phone, usluga, day, time)
    )
    conn.commit()

def get_zayvka(user_id):
    cursor.execute(
        "SELECT name, phone, usluga, day, time FROM clients WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()
    
def delete_zayvka(user_id):
    cursor.execute(
        "DELETE FROM clients WHERE user_id=?",
        (user_id,)
    )
    conn.commit()

def add_slot(day, time):
    cursor.execute(
        "INSERT INTO slots (day, time) VALUES (?, ?)",
        (day, time)
    )
    conn.commit()
    
def get_free_slot(day):
    cursor.execute(
        "SELECT time FROM slots WHERE day=? AND is_free=1",
        (day,)
    )
    return [row[0] for row in cursor.fetchall()]

def book_slot(day, time):
    cursor.execute(
        "UPDATE slots SET is_free=0 WHERE day=? AND time=?",
        (day, time)
    )
    conn.commit()
    
def get_all_clients():
    cursor.execute(
        "SELECT user_id FROM clients"
    )
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_clients_for_reminder(day, time):
    cursor.execute(
        "SELECT user_id, name, time FROM clients WHERE day LIKE ? AND time = ?",
        (f'%{day}%', time)
    )
    return cursor.fetchall()