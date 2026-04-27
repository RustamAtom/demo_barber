import sqlite3
from datetime import datetime

DB_NAME = "user.db"


# ====================== СОЗДАНИЕ ТАБЛИЦ ======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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
    conn.close()


# ====================== ЗАЯВКИ ======================
def save_zayvka(user_id, name, phone, usluga, day, time):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO clients(user_id, name, phone, usluga, day, time, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        """,
            (user_id, name, phone, usluga, day, time),
        )
        conn.commit()


def get_zayvka(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name, phone, usluga, day, time, status 
            FROM clients WHERE user_id=?
        """,
            (user_id,),
        )
        return cursor.fetchone()


def cancel_zayvka(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE clients SET status='cancelled' WHERE user_id=?", (user_id,)
        )
        conn.commit()


def get_all_zayvki():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, name, phone, usluga, day, time, status 
            FROM clients
        """
        )
        return cursor.fetchall()


# ====================== СЛОТЫ ======================
def add_slot(day, time):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO slots(day, time, is_free) VALUES (?, ?, 1)
        """,
            (day, time),
        )
        conn.commit()


def get_free_slot(day):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT time FROM slots 
            WHERE day=? AND is_free=1
        """,
            (day,),
        )
        return [row[0] for row in cursor.fetchall()]


def book_slot(day, time):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE slots SET is_free=0 
            WHERE day=? AND time=?
        """,
            (day, time),
        )
        conn.commit()


def free_slot(day, time):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE slots SET is_free=1 
            WHERE day=? AND time=?
        """,
            (day, time),
        )
        conn.commit()


# ====================== НАПОМИНАНИЯ И ОЧИСТКА ======================
def get_clients_for_reminder(target_time):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
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
        try:
            dt = datetime.strptime(f"{day} {time}", "%d.%m %H:%M")
            if 0 <= (dt - now).total_seconds() <= 7200:  # 2 часа
                result.append((user_id, name, time))
        except:
            pass
    return result


def clear_old_records():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Получаем активные записи
        cursor.execute("SELECT user_id, day, time FROM clients WHERE status='active'")
        rows = cursor.fetchall()
        now = datetime.now()
        for user_id, day, time in rows:
            try:
                dt = datetime.strptime(f"{day} {time}", "%d.%m %H:%M")
                if dt < now:
                    cursor.execute(
                        "UPDATE clients SET status='completed' WHERE user_id=?",
                        (user_id,),
                    )
            except:
                pass

        conn.commit()
        print("✅ Старые записи обработаны")


# Инициализация при импорте
init_db()
