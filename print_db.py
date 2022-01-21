import sqlite3

conn = sqlite3.connect("litterbox.db")

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

for table in tables:
    print('TABLE ', table)
    for row in conn.execute(f'SELECT * FROM {table[0]}'):
        print(row)