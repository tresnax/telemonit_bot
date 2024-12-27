import sqlite3

def create_database():
    conn = sqlite3.connect('db/telemonit_bot.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servers (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   password TEXT NOT NULL,
                   url TEXT NOT NULL)
                   ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_settings (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   interval INT NOT NULL,
                   cpu INT NOT NULL,
                   memory INT NOT NULL,
                   threads_id INTEGER NOT NULL)
                   ''')

    # Check and add columns if they do not exist
    cursor.execute("PRAGMA table_info(bot_settings)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'threads_id' not in columns:
        cursor.execute("ALTER TABLE bot_settings ADD COLUMN threads_id INTEGER NOT NULL DEFAULT 0")
    
    cursor.execute('INSERT INTO bot_settings (interval, cpu, memory, threads_id) VALUES (30, 80, 8, 0)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()