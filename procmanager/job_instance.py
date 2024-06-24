import subprocess
import platform
import signal
import sys
from copy import copy
from subprocess import TimeoutExpired, PIPE, STDOUT
from threading import Thread
import time
from datetime import datetime
import psutil
from procmanager import db
from procmanager.db import append_log
from procmanager import config
from procmanager import process_utils

JOB_DEFS = config.load_job_defs()
JOBS = {"hello": "echo hello",
        "sleep": "sleep 10",
        "sleeprepeat": "sleep 2; echo hello; sleep 2; echo hello2",
        "sleeperror": "echo hello; sleep 1; $host.ui.WriteErrorLine('I work in any PowerShell host'); sleep 2; echo hlo"}


# global process - i.e. one process per instance of the program
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
    def error(self):
        db.update_job_instance(_id=self.id, 
                               status='ERR', 
                               finished_at=datetime.now().timestamp())
    def cancel(self):
        db.update_job_instance(_id=self.id,
                               status='CNC',
                               finished_at=datetime.now().timestamp())

    def skip(self):
        db.update_job_instance(_id=self.id,
                               status='SKP',
                               finished_at=datetime.now().timestamp())

    def save_pid(self, pid):
        db.update_job_instance(_id=self.id,
                               pid=pid)
    #def check_process(self):
    #  NOTE if you uncomment this remember to assign the process to
    #    this job instance. but i dont think you should need this method.
    #    """ if running and start time was > than boot time.
    #    # just check if process running - boot time check
    #    # can happen at startup """
    #    if self.process and self.process.pid:
    #        return process_utils.is_running(self.process.pid)

def cleanup_jobs():
    boot_time = psutil.boot_time()  # TODO check when machine has timezones
    for ji in db.list_job_instances():
        if ji['status'] == 'NEW':
            if ji['started_at'] < boot_time:
                db.update_job_instance(_id = ji['id'], 
                                       status = 'CNC',
                                       finished_at = boot_time)
            elif ji['pid']:
                print(ji['pid'])
                db.is_process_running(ji['id'], ji['pid'])
               

def _stream_pipe(source, process):
    if source == 'stdout':
        pipe = process.stdout
    else:
        pipe = process.stderr
    # need out and err versions really
    #while True:
    #    line = pipe.readline()
    for line in pipe:
        print(line)
        append_log(__m.job_instance.id, source, line.decode())
    #if process.poll() is not None:
    #    return
    #    # time.sleep(1)


def _can_run(job_def: dict):
    for priority_job_name in job_def.get('givewayto', []):
        if db.is_job_running(priority_job_name):
            return False
    return True


def actually_run_job(jobname):
    # close cleanly on sigint
    signal.signal(signal.SIGINT, _signal_handler)

    print(JOB_DEFS)
    job_def = JOB_DEFS[jobname]
    # global process
    __m.job_instance = JobInstance(jobname)

    # Check to see if job is clear to run
    if not _can_run(job_def):
        __m.job_instance.skip()
        return

    if platform.system() == 'Windows':
        args = ['cmd', '/C']  
        args = ['powershell', '-c']  
    else:
        args = ['bash', '-c']
    args.append(job_def['command'])
    th_out, th_err = None, None
    if job_def:
        ''' SO code, simpler  '''
        with subprocess.Popen(args, stdout=PIPE, stderr=STDOUT, text=True) as process:
            __m.process = process
            __m.job_instance.save_pid(process.pid)
            for line in process.stdout:
                append_log(__m.job_instance.id, 'stdout', line)
        ''' Your code, bit naff, might have contention between stdout and stderr threads? '''
        '''
        process = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
        __m.process = process
        __m.job_instance.save_pid(process.pid)
        th_out = Thread(target=_stream_pipe, args=['stdout', process], daemon=True)
        th_out.start()
        th_err = Thread(target=_stream_pipe, args=['stderr', process], daemon=True)
        th_err.start()
        while True:
            # while (so := process.stdout.readline()):
            #     print(so)
            # while (se := process.stderr.readline()):
            #     print(se)
            if process.poll() is not None:
                time.sleep(0.5)
                break
            else:
                time.sleep(1)
        
        # for (o, e) in stream_from_process(process):
        #     print(o, e)
        '''
        print(process)
        print(process.pid)

        if process.returncode == 0:
            __m.job_instance.complete()
        else:
            __m.job_instance.error()
    '''
    if th_out:
        th_out.join()
    if th_err:
        th_err.join()
    '''
    # db.list_job_instances()


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
    # module_name = sys.modules[__name__]
    module_name = 'procmanager'
    args += ['-m', module_name]
    # args.append('--jobname')
    args.append('run')
    args.append(jobname)  # i.e. pm-cli run JOBNAME
    # args = [sys.executable] + args
    print(args)
    subprocess.Popen(args, cwd=config.RUN_DIR)
