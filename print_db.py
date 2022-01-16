import sqlite3

con = sqlite3.connect("litterbox.db")

for row in con.execute('SELECT * FROM EVENTS'):
    print(row)