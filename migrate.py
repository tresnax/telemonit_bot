import sqlite3
import os
import shutil

# Paths to the old and new databases
old_db_path = 'telemonit_bot.db'
new_db_dir = 'db'
new_db_path = os.path.join(new_db_dir, 'telemonit_bot.db')

# Ensure the new database directory exists
os.makedirs(new_db_dir, exist_ok=True)

# Copy the old database to the new location
shutil.copy2(old_db_path, new_db_path)

# Connect to the new database
conn = sqlite3.connect(new_db_path)
cursor = conn.cursor()

# Add threads_id column to bot_settings table if it doesn't exist
cursor.execute("PRAGMA table_info(bot_settings);")
columns = cursor.fetchall()
if not any(col[1] == 'threads_id' for col in columns):
    cursor.execute("ALTER TABLE bot_settings ADD COLUMN threads_id INTEGER DEFAULT 0;")

# Example of verifying the migration by listing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the new database:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()

print("Migration completed successfully.")
