import sqlite3
from dbcommands import *
import datetime
from datetime import timezone

conn = sqlite3.connect("litterbox.db")

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

for table in tables:
    print('TABLE ', table)
    for row in conn.execute(f'SELECT * FROM {table[0]}'):
        print(row)

'''conn = sqlite3.connect('litterbox.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
print(get_recent_box_uses(conn, 2)[0][2].timestamp())'''

'''insert_box_use_event(conn, datetime.datetime.now())'''


'''print(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
print(datetime.datetime.utcnow().timestamp())
print(datetime.datetime.now(timezone.utc))'''
