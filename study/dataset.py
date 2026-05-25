import sqlite3

DB_NAME = "history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_chat(user_msg, bot_msg):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO chats (user_message, bot_response) VALUES (?, ?)",
        (user_msg, bot_msg)
    )

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT user_message, bot_response FROM chats")
    rows = c.fetchall()

    conn.close()
    return rows