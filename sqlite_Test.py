import sqlite3

conn = sqlite3.connect("teleprogram.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")  # SELECT * FROM channels

tables = cursor.fetchall()

print("Таблиці у базі:", tables)

conn.close()
