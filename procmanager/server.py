from procmanager.web_server import start_web_server
from procmanager.scheduler import Scheduler
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

def start_scheduler():
    scheduler = Scheduler()
    #scheduler.add_job(jobname, schedule, command) #, args, kwargs)
    #scheduler.start_in_background()
    #async with AsyncScheduler() as scheduler:
    #    await scheduler.add_schedule(tick, IntervalTrigger(seconds=1))


def start_server(web_app=None):  # web_app this is to pass to the socketify initialisation interface
    start_scheduler()
    #start_web_server(web_app)
    start_web_server(web_app)

# Web server - bottle.py does stop on ctrl c but takes a very long time.
# import signal, sys

# def signal_handler(sig, frame):
#     print('caught signal')
#     sys.exit(0)

# print('setting signal')
# signal.signal(signal.SIGINT, signal_handler)