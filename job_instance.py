import subprocess
import platform
import signal
import sys
from subprocess import TimeoutExpired, PIPE, STDOUT
from threading import Thread
import time
from datetime import datetime
import db
from db import append_log


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

def stream_pipe(source, process):
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


def run_job(jobname):
    # close cleanly on sigint
    signal.signal(signal.SIGINT, signal_handler)
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
        th_out = Thread(target=stream_pipe, args=['stdout', process], daemon=True).start()
        th_err = Thread(target=stream_pipe, args=['stderr', process], daemon=True).start()
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


def signal_handler(sig, frame):
    # global process
    __m.process.kill()
    __m.job_instance.cancel()
    sys.exit(1)

