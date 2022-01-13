import datetime

def get_recent_event(conn):
    select_query = 'SELECT * FROM EVENTS ORDER BY ID DESC LIMIT 1'
    return conn.execute(select_query)

def insert_clean_event(conn, recent=None):
    if recent is None: recent = get_recent_event
    insert_query = 'INSERT INTO EVENTS(type, count, time) VALUES (?,?,?)'
    conn.execute(insert_query, (2, 0, datetime.datetime.now()))
    return recent.count
    
def insert_litterbox_event(conn, recent=None):
    if recent is None: recent = get_recent_event
    insert_query = 'INSERT INTO EVENTS(type, count, time) VALUES (?,?,?)'
    conn.execture(insert_query, (1, recent.count + 1, datetime.datetime.now()))
    