from datetime import datetime 
import os
import sqlite3
from procmanager import config
from procmanager import process_utils

DB_PATH = config.DB_PATH

def get_cursor():
    new_db = os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if new_db:
        create_db(conn, cur)
    return conn, cur

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

def insert_job_instance(_id, jobname):
    now_ts = datetime.now().timestamp()

    INSERT_JOB = f""" INSERT INTO job_instances VALUES (
                "{_id}",  "{jobname}", "NEW", {now_ts}, NULL, NULL 
                               );"""
    conn, cur = get_cursor()
    cur.execute(INSERT_JOB)
    conn.commit()    

def list_job_instances(jobname=None):
    LIST_JOBS = f"""select *, coalesce(finished_at, strftime('%s', 'now')) - started_at as running_length from job_instances"""
    if jobname:
        LIST_JOBS = f"""select *, finished_at - started_at from job_instances where jobname = "{jobname}" """
    conn, _ = get_cursor()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute(LIST_JOBS).fetchall()

    # print(res)
    print(cur.description)
    return (dict(r) for r in res)

def append_log(_id, line, source):
    # this could be slow, might want to put it in a file instead.
    source = 0 if source == 'stdout' else 1
    APPEND_LOG = f"""insert into ji_logs values 
                         ('{_id}', 
                          '{source}', 
                          '{line}');"""
    conn, cur = get_cursor()
    cur.execute(APPEND_LOG)
    conn.commit()


def create_job_instance(jobname) -> str:
    _id = f'{jobname}-{datetime.now().timestamp()}'
    insert_job_instance(_id, jobname)
    return _id

def update_job_instance(_id, **kwargs):
    update_clauses = []
    for k, v in kwargs.items():
        if isinstance(v, str):
            update_clauses.append(f"{k} = '{v}'")
        else: 
            update_clauses.append(f"{k} = '{v}'")
    update_clause = ', '.join(update_clauses)
    UPDATE_JOB_INSTANCE = f"""UPDATE job_instances set
        {update_clause}
        where id = '{_id}'"""
    conn, cur = get_cursor()
    print(UPDATE_JOB_INSTANCE)
    cur.execute(UPDATE_JOB_INSTANCE)
    conn.commit()


def is_job_running(jobname):
    """ Checks db if process running, then verifies if pid
       is really running, clears up if not """
    IS_JOB_RUNNING = f"""SELECT id, pid from job_instances where
         jobname = "{jobname}" and
         status = "NEW" """
    conn, cur = get_cursor()
    print(IS_JOB_RUNNING)
    res = list(cur.execute(IS_JOB_RUNNING).fetchall())
    running_result = False
    for _id, pid in res:
        if process_utils.is_running(pid):
            running_result = True
        else:
            update_job_instance(_id, status='DSC', finished_at=datetime.now().timestamp())
    print(running_result)
    return running_result
