import signal
import threading

from watchfiles import watch

from procmanager.web_server import start_web_server
from procmanager.scheduler import Scheduler
from procmanager.job_instance import cleanup_jobs
from procmanager.config import job_defs_path

import logging
log = logging.Logger('PythonProcessRunner')


# cannot use bottle because browsers just lock up the single thread.
# from bottle import route, run, template

# @route('/hello/<name>')
# def index(name):
#     return template('<b>Hello {{name}}</b>!', name=name)

# @route('/runjob/<jobname>')
# def runjob(jobname):

#     return f'Running job {jobname}'

# def start_web_server(host='localhost', port=8080):
#     #log.info
#     print('\033[32m' + 'Running Python Process Runner, spawning web server')
#     print('\033[39m') # and reset to default color
#     run(host=host, port=port )

def tick():
    from datetime import datetime
    print('hello the time is ' , datetime.now())

'''
class Watcher:
    def __init__(self, scheduler, config_dir):
        self.threads = []
        self.scheduler = scheduler
        self.config_dir = config_dir
        self.load_paths()

    def _clear_watchers(self):
        for t in self.threads:
            t.stop()
        self.threads = []

    def _start_watchers(self):
        for p in self.paths:
            self._watch_path(p)

    def _watch_it(self, path):
        for changes in watch(path, recursive=True):
            print(changes)
        print(f'{path} changed, reloading config')
        self._clear_watchers()
        self.load_paths()
        self.scheduler.reload()
        

    def _watch_path(self, path):
        t = threading.Thread(target=_watch_it, args=[path])
        t.start()

    def load_paths(self):
        self.paths = self.load_all_paths(config_dir)
        self.threads = []
        self.watch_paths_and_links()

    def watch_paths_and_links():
        pass #for paths
        '''

def _watch_config(scheduler, config_dir):
    print('running watch config')
    for changes in watch(config_dir, recursive=True, force_polling=True):
        print(changes)
        break
    print(f'Config directory {config_dir} changed, reloading...')
    scheduler.reload()
    _watch_config(scheduler, config_dir)

def spawn_watch_config(scheduler, config_dir):
    print('spawning watch config')
    t = threading.Thread(target=_watch_config, args=[scheduler, config_dir])
    t.start()
    print("started thread")
    return t
    

def start_scheduler():
    cleanup_jobs()
    scheduler = Scheduler()
    print("spawn thread")
    spawn_thread = spawn_watch_config(scheduler, job_defs_path())
    #scheduler.add_job(jobname, schedule, command) #, args, kwargs)
    #scheduler.start_in_background()
    #async with AsyncScheduler() as scheduler:
    #    await scheduler.add_schedule(tick, IntervalTrigger(seconds=1))


def start_server(web_app=None, args=None):  
        start_scheduler()

        signal.pause()

        #start_web_server(web_app)
        # start_web_server(web_app, args)

# Web server - bottle.py does stop on ctrl c but takes a very long time.
# import signal, sys

# def signal_handler(sig, frame):
#     print('caught signal')
#     sys.exit(0)

# print('setting signal')
# signal.signal(signal.SIGINT, signal_handler)
