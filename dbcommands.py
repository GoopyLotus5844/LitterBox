import datetime
from select import select

def get_recent_box_use(conn):
    select_query = 'SELECT * FROM BOX_USE ORDER BY ID DESC LIMIT 1'
    return conn.execute(select_query).fetchone()

def get_recent_box_uses(conn, limit):
    select_query = 'SELECT * FROM BOX_USE ORDER BY ID DESC LIMIT {}'.format(limit)
    return conn.execute(select_query).fetchall()

def get_recent_clean(conn):
    select_query = 'SELECT * FROM CLEAN ORDER BY ID DESC LIMIT 1'
    return conn.execute(select_query).fetchone()

def get_user_config(conn):
    select_query = 'SELECT * FROM CONFIG LIMIT 1'
    return conn.execute(select_query).fetchone()

def get_avg_uses_before_clean(conn, sample):
    select_query = f'SELECT * FROM CLEAN ORDER BY ID DESC LIMIT {sample}'
    result = conn.execute(select_query)

    total_uses = 0
    total_events = 0
    for row in result:
        total_events += 1
        total_uses += row[1]

    if total_events == 0: return 0
    return total_uses / total_events

def get_avg_daily_uses(conn, sample):
    select_query = f'SELECT * FROM BOX_USE ORDER BY ID DESC LIMIT {sample}'
    result = conn.execute(select_query)

    total_days = 0
    day = 0
    total_uses = 0
    for row in result:
        if row[1] == 0: continue
        if row[2].day != day:
            total_days += 1
            day = row[2].day
        total_uses += 1

    if total_days == 0: return total_uses
    return total_uses / total_days
    
def insert_clean_event(conn):
    count = get_recent_box_use(conn)[1]
    now = datetime.datetime.now()
    insert_query = 'INSERT INTO CLEAN(count, time) VALUES (?,?)'

    conn.execute(insert_query, (count, now))

    insert_query = 'INSERT INTO BOX_USE(count, time) VALUES (?,?)'
    conn.execute(insert_query, (0, now))

    conn.commit()
    return count
    
def insert_box_use_event(conn):
    recent = get_recent_box_use(conn)
    count = recent[1] + 1
    insert_query = 'INSERT INTO BOX_USE(count, time) VALUES (?,?)'
    conn.execute(insert_query, (count, datetime.datetime.now()))
    conn.commit()
    return count
    
def update_cat_name(conn, name):
    insert_query = 'UPDATE CONFIG SET name = ?'
    conn.execute(insert_query, (name,))
    conn.commit()