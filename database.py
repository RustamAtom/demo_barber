import sqlite3

conn = sqlite3.connect("user.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()
