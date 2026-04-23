import sqlite3
from datetime import datetime

conn = sqlite3.connect("user.db", check_same_thread=False)
cursor = conn.cursor()

# --- ЗАЯВКИ ---
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS clients(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    usluga TEXT,
    day TEXT,
    time TEXT,
    status TEXT DEFAULT 'active'
)
"""
)

# --- СЛОТЫ ---
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS slots(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    time TEXT,
    is_free INTEGER DEFAULT 1
)
"""
)

conn.commit()


# ------------------------
# СОХРАНЕНИЕ ЗАЯВКИ
# ------------------------
def save_zayvka(user_id, name, phone, usluga, day, time):
    cursor.execute(
        """
    INSERT OR REPLACE INTO clients(user_id, name, phone, usluga, day, time, status)
    VALUES (?, ?, ?, ?, ?, ?, 'active')
    """,
        (user_id, name, phone, usluga, day, time),
    )
    conn.commit()


# ------------------------
# ПОЛУЧИТЬ ЗАЯВКУ
# ------------------------
def get_zayvka(user_id):
    cursor.execute(
        """
    SELECT name, phone, usluga, day, time, status 
    FROM clients WHERE user_id=?
    """,
        (user_id,),
    )
    return cursor.fetchone()


# ------------------------
# УДАЛИТЬ (ОТМЕНА)
# ------------------------
def cancel_zayvka(user_id):
    cursor.execute(
        """
    UPDATE clients SET status='cancelled' WHERE user_id=?
    """,
        (user_id,),
    )
    conn.commit()


# ------------------------
# ЗАВЕРШИТЬ (ПОСЛЕ ВРЕМЕНИ)
# ------------------------
def complete_zayvka(user_id):
    cursor.execute(
        """
    UPDATE clients SET status='completed' WHERE user_id=?
    """,
        (user_id,),
    )
    conn.commit()


# ------------------------
# СЛОТЫ
# ------------------------
def add_slot(day, time):
    cursor.execute(
        """
    INSERT INTO slots(day, time, is_free)
    VALUES (?, ?, 1)
    """,
        (day, time),
    )
    conn.commit()


def get_free_slot(day):
    cursor.execute(
        """
    SELECT time FROM slots 
    WHERE day=? AND is_free=1
    """,
        (day,),
    )
    return [row[0] for row in cursor.fetchall()]


def book_slot(day, time):
    cursor.execute(
        """
    UPDATE slots SET is_free=0 
    WHERE day=? AND time=?
    """,
        (day, time),
    )
    conn.commit()


def free_slot(day, time):
    cursor.execute(
        """
    UPDATE slots SET is_free=1 
    WHERE day=? AND time=?
    """,
        (day, time),
    )
    conn.commit()


# ------------------------
# НАПОМИНАНИЯ
# ------------------------
def get_clients_for_reminder(target_time):
    cursor.execute(
        """
    SELECT user_id, name, day, time 
    FROM clients 
    WHERE status='active'
    """
    )
    rows = cursor.fetchall()

    result = []
    now = datetime.now()

    for user_id, name, day, time in rows:
        dt = datetime.strptime(f"{day} {time}", "%d.%m %H:%M")

        # если до записи осталось ~2 часа
        if 0 <= (dt - now).total_seconds() <= 120:
            result.append((user_id, name, time))

    return result


# ------------------------
# АВТОЗАКРЫТИЕ
# ------------------------
def clear_old_records():
    cursor.execute(
        """
    SELECT user_id, day, time FROM clients WHERE status='active'
    """
    )
    rows = cursor.fetchall()

    now = datetime.now()

    for user_id, day, time in rows:
        dt = datetime.strptime(f"{day} {time}", "%d.%m %H:%M")

        if dt < now:
            cursor.execute(
                """
            UPDATE clients SET status='completed' WHERE user_id=?
            """,
                (user_id,),
            )

    conn.commit()


# ------------------------
# СПИСОК
# ------------------------
def get_all_zayvki():
    cursor.execute(
        """
    SELECT user_id, name, phone, usluga, day, time, status 
    FROM clients
    """
    )
    return cursor.fetchall()


def get_all_clients():
    cursor.execute("SELECT user_id FROM clients")
    return [row[0] for row in cursor.fetchall()]
