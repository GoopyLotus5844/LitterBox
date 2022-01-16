import datetime

def get_recent_event(conn):
    select_query = 'SELECT * FROM EVENTS ORDER BY ID DESC LIMIT 1'
    return conn.execute(select_query).fetchone()

def insert_clean_event(conn):
    count = get_recent_event(conn)[2]
    insert_query = 'INSERT INTO EVENTS(type, count, time) VALUES (?,?,?)'
    conn.execute(insert_query, (2, 0, datetime.datetime.now()))
    conn.commit()
    return count
    
def insert_litterbox_event(conn, recent=None):
    if recent is None: recent = get_recent_event(conn)
    count = recent[2] + 1
    insert_query = 'INSERT INTO EVENTS(type, count, time) VALUES (?,?,?)'
    conn.execute(insert_query, (1, count, datetime.datetime.now()))
    conn.commit()
    return count
    