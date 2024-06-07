## Allows user to add and remove jobs dynamically.
import os
import toml
from threading import RLock
l = RLock()

from procmanager.config import DYN_CONFIG_FILE
DYN_CONFIG = toml.load(DYN_CONFIG_FILE) if os.path.exists(DYN_CONFIG_FILE) else {}

def remove_from_dynamic_config(jobname):
    if jobname in DYN_CONFIG:
        del DYN_CONFIG[jobname]

def _write_config():
    # should get a lock for this.
    l.acquire()
    try:
        with open(DYN_CONFIG_FILE, 'w') as f:
            toml.dump(DYN_CONFIG, f)
    except FileNotFoundError:
        # Doesnt exist, fine.
        pass
    finally:
        l.release()

def add_to_dynamic_config(jobname, schedule, command):
    DYN_CONFIG[jobname] = {'jobname': jobname,
                            'schedule': schedule,
                            'command': command}
    _write_config()