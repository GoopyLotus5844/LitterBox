import sqlite3

conn = sqlite3.connect("litterbox.db")

print('TABLE BOX_USE')
for row in conn.execute('SELECT * FROM BOX_USE'):
    print(row)

print('TABLE CLEAN')
for row in conn.execute('SELECT * FROM CLEAN'):
    print(row)