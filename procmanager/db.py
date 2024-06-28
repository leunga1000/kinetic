from datetime import datetime 
import os
import sqlite3
from procmanager import config
from procmanager import process_utils
from procmanager.config import LOG_DIR

DB_PATH = config.DB_PATH


def _clear_db(): # for testing
    conn, cur = get_cursor()
    cur.execute("drop table if exists job_instances;")
    cur.execute("""drop table if exists ji_logs;""")
    conn.commit()

def create_db(conn, cur):
    JOB_INSTANCES =  """Create table if not exists job_instances (id VARCHAR, 
                 jobname VARCHAR,
                 status VARCHAR,
                 started_at INT,
                 finished_at INT,
                 pid INT
                 );"""
    JI_LOGS = """Create table if not exists ji_logs (
                         id VARCHAR, 
                         source INT, line VARCHAR
                        );""" # 0 for stdout 1 for stderr
    
    cur.execute(JOB_INSTANCES)
    cur.execute(JI_LOGS)
    conn.commit()

class C:
    """ Holds connection. TODO remove not sure it helps """
    def __init__(self):
        new_db = not os.path.exists(DB_PATH)
        self.conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=10) # autocommit
        if new_db:
            create_db(self.conn, self.conn.cursor())

c = C()


def get_cursor():
    #new_db = os.path.exists(DB_PATH)
    #conn = sqlite3.connect(DB_PATH, isolation_level=None) # autocommit
    #if new_db:
    #    create_db(conn, cur)
   
    #cur = c.conn.cursor()
    #return c.conn, cur
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=10) # autocommit
    return conn, conn.cursor()

if not os.path.exists(DB_PATH):
    conn, cursor = get_cursor()
    create_db(conn, cursor)

def insert_job_instance(_id, jobname):
    now_ts = datetime.now().timestamp()

    INSERT_JOB = f""" INSERT INTO job_instances VALUES (
                ?,  ?, "NW", ?, NULL, NULL 
                               );"""
    conn, cur = get_cursor()
    cur.execute(INSERT_JOB, (_id, jobname, now_ts))
    conn.commit()    

def list_job_instances(jobname=None, top_down=False):
    by_jobname = 'where jobname = ?' if jobname else ''
    order_by = 'order by started_at desc' if top_down else ''
    LIST_JOBS = f"""select *, coalesce(finished_at, strftime('%s', 'now')) - started_at as running_length from job_instances {by_jobname} {order_by}"""
    conn, _ = get_cursor()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if jobname:
        res = cur.execute(LIST_JOBS, jobname).fetchall()
    else:
        res = cur.execute(LIST_JOBS).fetchall()
    # print(res)
    #print(cur.description)
    return (dict(r) for r in res)

def append_log(_id, source, line):
    log_name = _id + '.log'
    path = os.path.join(LOG_DIR, log_name)
    with open(path, 'a') as f:
        f.write(line)
    # this could be slow, might want to put it in a file instead.
    #source = 0 if source == 'stdout' else 1
    #APPEND_LOG = f"""insert into ji_logs values 
    #                     (?, 
    #                      ?, 
    #                      ?);"""
    #print(APPEND_LOG)
    #conn, cur = get_cursor()
    #cur.execute(APPEND_LOG, (_id, source, line.rstrip('\n')))
    #conn.commit()


def create_job_instance(jobname) -> str:
    _id = f'{jobname}-{datetime.now().timestamp()}'
    insert_job_instance(_id, jobname)
    return _id

def update_job_instance(_id, **kwargs):
    update_clauses = []
    for k, v in kwargs.items():
        update_clauses.append(f"{k} = ?")
    
    update_clause = ', '.join(update_clauses)
    UPDATE_JOB_INSTANCE = f"""UPDATE job_instances set
        {update_clause}
        where id = ?; """
    conn, cur = get_cursor()
    print(UPDATE_JOB_INSTANCE)
    #conn.set_trace_callback(print)
    cur.execute(UPDATE_JOB_INSTANCE, (*list(kwargs.values()), _id))
    conn.commit()


def is_process_running(_id, pid):
    running_result = False
    if process_utils.is_running(pid):
        running_result = True
    else:
        update_job_instance(_id, status='DC', finished_at=datetime.now().timestamp())
    return running_result

def is_job_running(jobname):
    """ Checks db if process running, then verifies if pid
       is really running, clears up if not """
    IS_JOB_RUNNING = f"""SELECT id, pid from job_instances where
         jobname = ? and
         (status = 'NW' or status = 'GO') """
    conn, cur = get_cursor()
    print(IS_JOB_RUNNING)
    res = list(cur.execute(IS_JOB_RUNNING, (jobname,)).fetchall())
    running_result = False
    for _id, pid in res:
        if is_process_running(_id, pid):
            running_result = True
            #poll_pid(parent_pid)  # poll parent to avoid bob/zombies.
    print(running_result)
    return running_result
