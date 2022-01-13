import datetime
import sqlite3

con = sqlite3.connect("test.db")

with con:
    con.execute('''CREATE TABLE EVENTS
                 (ID INTEGER PRIMARY KEY,
                  type INT NOT NULL,
                  time TIMESTAMP NOT NULL)''')

    insertQuery = 'INSERT INTO EVENTS(type, time) VALUES (?,?)'
    con.execute(insertQuery, (2, datetime.datetime.now()))

    for row in con.execute('SELECT * FROM EVENTS'):
        print(row)