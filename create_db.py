import sqlite3
from sqlite3 import Error
import datetime

from sms_server import connect_db

def create_db(conn):
    conn.execute('''CREATE TABLE BOX_USE
        (ID INTEGER PRIMARY KEY,
        count INT NOT NULL,
        time TIMESTAMP NOT NULL)''')
    insertQuery = 'INSERT INTO BOX_USE(count, time) VALUES (?,?)'
    conn.execute(insertQuery, (0, datetime.datetime.now()))
    conn.execute('''CREATE TABLE CLEAN
        (ID INTEGER PRIMARY KEY,
        count INT NOT NULL,
        time TIMESTAMP NOT NULL)''')
    add_config_table(conn)

def add_config_table(conn):
    conn.execute('''CREATE TABLE CONFIG
       (name TEXT NOT NULL)''')
    insertQuery = 'INSERT INTO CONFIG(name) VALUES (?)'
    conn.execute(insertQuery, ("Your Cat",))

def new_config_table(conn):
    conn.execute('DROP TABLE CONFIG')
    conn.execute('''CREATE TABLE CONFIG
        (name TEXT NOT NULL,
        range INTEGER NOT NULL,
        reminder INTEGER NOT NULL,
        cleanPause INTEGER NOT NULL)''')
    insertQuery = 'INSERT INTO CONFIG(name, range, reminder, cleanPause) VALUES (?, ?, ?, ?)'
    conn.execute(insertQuery, ("Your Cat", 50, 3, 300))

if __name__ == '__main__':
    conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    command = input()
    if command == '0':
        create_db(conn)
    elif command == '1':
        add_config_table(conn)
    elif command == '2':
        new_config_table(conn)
    conn.commit()
    conn.close()
