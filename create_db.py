import sqlite3
from sqlite3 import Error
import datetime

def make_table(conn):
    conn.execute('''CREATE TABLE BOX_USE
                 (ID INTEGER PRIMARY KEY,
                  count INT NOT NULL,
                  time TIMESTAMP NOT NULL)''')

    conn.execute('''CREATE TABLE CLEAN
                (ID INTEGER PRIMARY KEY,
                count INT NOT NULL,
                time TIMESTAMP NOT NULL)''')

def starter_entry(conn):
    insertQuery = 'INSERT INTO BOX_USE(count, time) VALUES (?,?)'
    conn.execute(insertQuery, (0, datetime.datetime.now()))

if __name__ == '__main__':
    conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    make_table(conn)
    starter_entry(conn)
    conn.commit()
    conn.close()
