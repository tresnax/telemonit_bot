import sqlite3

def create_database():
    conn = sqlite3.connect('telemonit_bot.db')
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
                   memory INT NOT NULL)
                   ''')
    
    cursor.execute('INSERT INTO bot_settings (interval, cpu, memory) VALUES (30, 80, 8)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()