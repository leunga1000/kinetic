import subprocess
import platform
import signal
import sys
from copy import copy
from subprocess import TimeoutExpired, PIPE, STDOUT
from threading import Thread
import time
from datetime import datetime
from procmanager import db
from procmanager.db import append_log
from procmanager import config

JOBS = {"hello": "echo hello",
        "sleep": "sleep 10",
        "sleeprepeat": "sleep 2; echo hello; sleep 2; echo hello2",
        "sleeperror": "echo hello; sleep 1; $host.ui.WriteErrorLine('I work in any PowerShell host'); sleep 2; echo hlo"}

# global process
class Box:
    pass
__m = Box()

class JobInstance:
    def __init__(self, jobname):
        self.jobname = jobname
        self.id = db.create_job_instance(jobname)

    def complete(self):
        db.update_job_instance(_id=self.id,
                               status='OKC', 
                               finished_at=datetime.now().timestamp())

def _stream_pipe(source, process):
    if source == 'stdout':
        pipe = process.stdout
    else:
        pipe = process.stderr
    # need out and err versions really
    while True:
        line = pipe.readline()
        print(line)
        append_log(__m.job_instance.id, source, line)
        if process.poll() is not None:
            return
        time.sleep(1)


def actually_run_job(jobname):
    # close cleanly on sigint
    signal.signal(signal.SIGINT, _signal_handler)
    # global process

    job = JOBS[jobname]
    __m.job_instance = JobInstance(jobname)
    if platform.system() == 'Windows':
        args = ['cmd', '/C']  
        args = ['powershell', '-c']  
    else:
        args = ['bash', '-c']
    args.append(job)
    if job:
        process = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
        __m.process = process
        th_out = Thread(target=_stream_pipe, args=['stdout', process], daemon=True).start()
        th_err = Thread(target=_stream_pipe, args=['stderr', process], daemon=True).start()
        while True:
            # while (so := process.stdout.readline()):
            #     print(so)
            # while (se := process.stderr.readline()):
            #     print(se)
            if process.poll() is not None:
                break
            else:
                time.sleep(1)
        
        # for (o, e) in stream_from_process(process):
        #     print(o, e)
    print(process)
    print(process.pid)
    __m.job_instance.complete()
    db.list_job_instances()


def _signal_handler(sig, frame):
    # global process
    __m.process.kill()
    __m.job_instance.cancel()
    sys.exit(1)



def run_job(jobname):
    """ Interface to the job running code.
    Spawns an instance of this code in job running mode """
    
    args = copy(sys.argv)
    
    # if args[1] == '-m':
    #     args.pop(1)
    # if args[1] == 'socketify':
    #     args.pop(1)
    # args.remove('socketify')
    args = [sys.executable]
    module_name = sys.modules[__name__]
    args += ['-m', module_name]
    args.append('--jobname')
    args.append(jobname)
    # args = [sys.executable] + args
    print(args)
    subprocess.Popen(args, cwd=config.RUN_DIR)