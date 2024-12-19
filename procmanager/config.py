import os
import glob
import json
import toml

# APP Config
AUTORELOAD = True
ACCOUNTS = {'example1': {'api_key': '13131'}}
RUN_DIR = os.path.expanduser('~')  # os.path.dirname(os.path.realpath(__file__)) 
# JOBS CONFIG

BASE_PATH = os.path.expanduser(os.path.join('~', '.kin_dir'))
os.makedirs(BASE_PATH, exist_ok=True)
HOME_BIN = os.path.expanduser(os.path.join('~', 'bin'))
os.makedirs(HOME_BIN, exist_ok=True)
JOB_DEFS_PATH = os.path.join(BASE_PATH, 'job_defs')
os.makedirs(JOB_DEFS_PATH, exist_ok=True)
DYN_CONFIG_FILE = os.path.join(JOB_DEFS_PATH, 'dyn_config.toml')

LOG_DIR = os.path.join(BASE_PATH, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# UPDATE CONFIG
KINETIC_BINARY_URL_X64 = 'https://kinetic.icedb.info/x64/kin'


def config_files():
    # CONFIG_FILES = 
    return glob.glob(f'{JOB_DEFS_PATH}/**', recursive=True)

def job_defs_path():
    return JOB_DEFS_PATH

# DB
DB_FILENAME = 'ppr.db'
DB_PATH = os.path.join(BASE_PATH, DB_FILENAME)

def load_job_defs():
    # returns dictionary job defs
    job_defs = {}
    print(f'..Loading defs from {JOB_DEFS_PATH}')
    for path in config_files():
        if not os.path.isfile(path):
            continue
        with open(path, 'r') as fh:
            if path.endswith('json'):
                d = json.load(fh)
            elif path.endswith('toml'):
                d = toml.load(fh)
            else:
                print(f'..Extension {path} not yet implemented')
                continue
            # yaml, ini
        # merge dictionaries
        job_defs = dict(list(job_defs.items()) + list(d.items()))
    return job_defs
    
