import sqlite3
from sqlite3 import Error
import datetime

def make_table(conn):
    conn.execute('''CREATE TABLE EVENTS
                 (ID INTEGER PRIMARY KEY,
                  type INT NOT NULL,
                  time TIMESTAMP NOT NULL)''')

def insert_entry(conn):
    insertQuery = 'INSERT INTO EVENTS(type, time) VALUES (?,?)'
    conn.execute(insertQuery, (2, datetime.datetime.now()))

if __name__ == '__main__':
    conn = sqlite3.connect('./db/test.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    #make_table(conn)
    insert_entry(conn)
    conn.commit()
    conn.close()