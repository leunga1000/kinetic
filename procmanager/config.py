import os
import glob
import json
import toml

# APP Config
AUTORELOAD = True
ACCOUNTS = {'example1': {'api_key': '13131'}}
RUN_DIR = os.path.expanduser('~')  # os.path.dirname(os.path.realpath(__file__)) 
# JOBS CONFIG

BASE_PATH = os.path.expanduser(os.path.join('~', 'process_runner_conf'))
os.makedirs(BASE_PATH, exist_ok=True)
JOB_DEFS_PATH = os.path.join(BASE_PATH, 'job_defs')
os.makedirs(JOB_DEFS_PATH, exist_ok=True)
DYN_CONFIG_FILE = os.path.join(JOB_DEFS_PATH, 'dyn_config.toml')

CONFIG_FILES = glob.glob(f'{JOB_DEFS_PATH}/**', recursive=True)
# DB
DB_FILENAME = 'ppr.db'
DB_PATH = os.path.join(BASE_PATH, DB_FILENAME)

def load_job_defs():
    # returns dictionary job defs
    job_defs = {}
    for path in CONFIG_FILES:
        print(path)
        if not os.path.isfile(path):
            continue
        with open(path, 'r') as fh:
            if path.endswith('json'):
                d = json.load(fh)
            elif path.endswith('toml'):
                d = toml.load(fh)
            # yaml, ini
        # merge dictionaries
        job_defs = dict(list(job_defs.items()) + list(d.items()))
    return job_defs
    
