import sqlite3
from datetime import datetime


def db_connection():
    conn = sqlite3.connect('db/telemonit_bot.db')

    return conn


def log_connection():
    conn = sqlite3.connect('db/telemonit_log.db')

    return conn


def add_server(username: str, password: str, url: str) -> None :
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO servers (username, password, url) 
                   VALUES (?, ?, ?)''', (username, password, url, )
                   )

    conn.commit()
    conn.close


def del_server(id: int) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM servers WHERE id=? ', (id, ))

    conn.commit()
    conn.close()


def add_thread(thread_id: int) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO threads (threads_id) VALUES (?)', (thread_id, ))

    conn.commit()
    conn.close()


def del_thread(thread_id: int) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM threads WHERE threads_id=?', (thread_id, ))

    conn.commit()
    conn.close()


def list_server():
    conn =db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM servers')
    row = cursor.fetchall()

    conn.close()
    return row


def bot_setting() -> list:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bot_settings WHERE id=1')
    row = cursor.fetchone()

    conn.close()
    return row


def set_setting(name: str, value: int) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    sql = f"UPDATE bot_settings SET {name}=? WHERE id=?"
    cursor.execute(sql, (value, 1))
    
    conn.commit()
    conn.close()


def log_alert(server_id, service, metric, value, status):
    conn = log_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO server_logs (timestamp, server_id, service, metric, value, status) VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), server_id, service, metric, value, status))

    conn.commit()
    conn.close()