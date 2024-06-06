from datetime import datetime 
import sqlite3
FILENAME = 'ppr.db'

def get_cursor():
    conn = sqlite3.connect(FILENAME)
    cur = conn.cursor()
    return conn, cur

def _clear_db(): # for testing
    conn, cur = get_cursor()
    cur.execute("drop table if exists job_instances;")
    cur.execute("""drop table if exists ji_logs;""")
    conn.commit()

def create_db():
    JOB_INSTANCES =  """Create table if not exists job_instances (id VARCHAR, 
                 jobname VARCHAR,
                 status VARCHAR,
                 started_at INT,
                 finished_at INT
                 );"""
    JI_LOGS = """Create table if not exists ji_logs (
                         id VARCHAR, 
                         source INT, line VARCHAR
                        );""" # 0 for stdout 1 for stderr
    conn, cur = get_cursor() 
    cur.execute(JOB_INSTANCES)
    cur.execute(JI_LOGS)
    conn.commit()

def insert_job_instance(_id, jobname):
    now_ts = datetime.now().timestamp()
    INSERT_JOB = f""" INSERT INTO job_instances VALUES ("{_id}",  "{jobname}", "NEW", {now_ts}, NULL);"""
    conn, cur = get_cursor()
    cur.execute(INSERT_JOB)
    conn.commit()    

def list_job_instances(jobname=None):
    LIST_JOBS = f"""select *, finished_at - started_at from job_instances"""
    if jobname:
        LIST_JOBS = f"""select *, finished_at - started_at from job_instances where jobname = "{jobname}" """
    res = get_cursor()[1].execute(LIST_JOBS).fetchall()

    print(res)
    return res

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