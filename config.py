import os
import glob
import json
import toml

# APP Config
AUTORELOAD = True
ACCOUNTS = {'example1': {'api_key': '13131'}}


# JOBS CONFIG

BASE_PATH = os.path.expanduser(os.path.join('~', 'process_runner_conf'))
os.makedirs(BASE_PATH, exist_ok=True)
JOB_DEFS_PATH = os.path.join(BASE_PATH, 'job_defs')
os.makedirs(JOB_DEFS_PATH, exist_ok=True)
DYN_CONFIG_FILE = os.path.join(JOB_DEFS_PATH, 'dyn_config.toml')

CONFIG_FILES = glob.glob(JOB_DEFS_PATH, recursive=True)


def load_config():
    # returns dictionary job defs
    job_defs = {}
    for path in CONFIG_FILES:
        print(path)
        if not os.path.isfile(path):
            continue
        with open(f, 'r') as fh:
            if fh.endswith('json'):
                d = json.load(f)
            elif fh.endswith('toml'):
                d = toml.load(f)
            # yaml, ini
        # merge dictionaries
        job_defs = dict(list(job_defs.items()) + list(d.items()))
    return job_defs
    