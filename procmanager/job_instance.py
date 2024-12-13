import subprocess
import platform
import signal
import sys
from copy import copy
import os
from subprocess import TimeoutExpired, PIPE, STDOUT
from threading import Thread
import time
from datetime import datetime
import psutil
import dateparser
from procmanager import db
from procmanager import config
from procmanager import process_utils
from procmanager.config import LOG_DIR


JOBS = {"hello": "echo hello",
        "sleep": "sleep 10",
        "sleeprepeat": "sleep 2; echo hello; sleep 2; echo hello2",
        "sleeperror": "echo hello; sleep 1; $host.ui.WriteErrorLine('I work in any PowerShell host'); sleep 2; echo hlo"}


# global process - i.e. one process per instance of the program
class Box:
    pass
__m = Box()


class JobInstance:
    def __init__(self, jobname, _id=None):
        self.jobname = jobname

        if _id:
            self.id = _id
        else:
            self.id = db.create_job_instance(jobname)

    def complete(self):
        db.update_job_instance(_id=self.id,
                               status='OK', 
                               finished_at=datetime.now().timestamp())
    def error(self):
        db.update_job_instance(_id=self.id, 
                               status='ER', 
                               finished_at=datetime.now().timestamp())
    def cancel(self):
        db.update_job_instance(_id=self.id,
                               status='CL',
                               finished_at=datetime.now().timestamp())

    def skip(self):
        db.update_job_instance(_id=self.id,
                               status='SK',
                               finished_at=datetime.now().timestamp())

    def go(self):
        db.update_job_instance(_id=self.id,
                               status='GO',
                               )

    def had_errors(self):
        db.update_job_instance(_id=self.id,
                               had_errors=True,
                               )

    def timed_out(self):
        db.update_job_instance(_id=self.id,
                               status='TI',
                               finished_at=datetime.now().timestamp(),
                               )

    def stopped_by_boot(self, boot_time):
        boot_time = boot_time or datetime.now().timestamp()
        db.update_job_instance(_id=self.id,
                               status='SB',
                               finished_at=boot_time,
                               )

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

def wait_pid(pid):
    if not pid:
        return
    try:
        psutil.Process(pid).wait(timeout=1)
    except Exception as e:
        print(e)

def clear_zombie(parent_pid, system_pids=None):
    if not parent_pid:
        return

    if system_pids and parent_pid not in system_pids: 
        return

    try:
        parent_process = psutil.Process(parent_pid)
    except Exception as e:
        print(f'Couldn\'t get process for pid {parent_pid}')
        return
    pparents = []
    pp = parent_process.parent()
    if pp:
        pparents.append(pp)
        ppp = pp.parent()
        if ppp:
            pparents.append(ppp)

    print('..waiting for processes to exit')
    for p in [parent_process, *pparents, *parent_process.children()]:
        if p.status() == psutil.STATUS_ZOMBIE:
            print('polling zombie')
            p.is_running()

def cleanup_jobs():
    boot_time = psutil.boot_time()  # TODO check when machine has timezones
    system_pids = psutil.pids()
    for ji in db.list_job_instances():
        if ji['status'] in ['NW', 'GO']:
            if ji['started_at'] < boot_time:
                ji_object = JobInstance(ji.get('jobname'), ji['id'])
                ji_object.stopped_by_boot(boot_time)
                #db.update_job_instance(_id = ji['id'], 
                #                       status = 'SB',
                #                       finished_at = boot_time)
            elif ji['pid']:
                print(ji['pid'])
                db.is_process_running(ji['id'], ji['pid'])
        clear_zombie(ji['pid'], system_pids)


def get_timeout_dt(timeout):
    """ Is dynamic - returns next timeout datetime for timeout expression """
    if not timeout:
        return None

    """ Default to seconds """
    if timeout and type(timeout) == int or timeout.isnumeric():
        timeout = f'in {timeout} seconds'
    elif not timeout.lower().startswith('in'):
        timeout = f'in {timeout}'
    try:
        return dateparser.parse(timeout)
    except Exception as e:
        print(e)
        print(f'Couldn\'t parser timeout expression {timeout}')


def get_log_path(_id):
    log_name = _id + '.log'
    return os.path.join(LOG_DIR, log_name)

def append_log(_id, source, line):
    log_path = get_log_path(_id)

    if source == 'stderr':
        line = f'ERROR: {line}'

    with open(log_path, 'a') as f:
        f.write(line)


def zip_log(_id):
    log_path = get_log_path(_id)
    try:
        # blocking
        # os.system(f'gzip {log_path}')

        # non blocking
        args = ['gzip', log_path]
        p = subprocess.Popen(args, cwd=config.LOG_DIR) #, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(e)


               
def _stream_pipe(source, process, job_instance):
    if source == 'stdout':
        pipe = process.stdout
    else:
        pipe = process.stderr
    # need out and err versions really
    #while True:
    #    line = pipe.readline()
    started_output = False
    has_errors = False
    for line in pipe:
        print(line)
        #if not started_output:
        #    job_instance.go()
        #    started_output = True

        #if source =='stdout':
        if not has_errors and source =='stderr':
            job_instance.had_errors()
            has_errors = True
        
        append_log(job_instance.id, source, line.decode())
        #append_log(job_instance.id, 'stdout', line)
    #if process.poll() is not None:
    #    return
    #    # time.sleep(1)


def _can_run(job_def: dict):
    for priority_job_name in job_def.get('givewayto', []):
        if db.is_job_running(priority_job_name):
            return False
    return True


def _run_following_jobs(follow_on_type, prev_job_id, prev_job_def):
    """ 
    Run next jobs if there was no error.. 
    'next' if program exited without error 
    and 'error' if it did"""

    following_jobs = prev_job_def.get(follow_on_type)
    if isinstance(following_jobs, str):
        run_job(following_jobs)
    elif following_jobs is not None:
        for job in following_jobs:
            run_job(job)

def _kill_process_tree(pid):
    process = psutil.Process(pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def actually_run_job(jobname):
    # close cleanly on sigint
    def _signal_handler(sig, frame):
        if process and process.pid:
            ppid = psutil.Process(process.pid).ppid() 
            if ppid == os.getpid():
                process.kill()
                print('cancelling' )
                job_instance.cancel()
        sys.exit(1)
    signal.signal(signal.SIGINT, _signal_handler)


    JOB_DEFS = config.load_job_defs()
    print(JOB_DEFS)
    job_def = JOB_DEFS[jobname]
    timeout_dt = get_timeout_dt(job_def.get('timeout'))
    # global process for each job 
    job_instance = JobInstance(jobname)
    # store it for the signal_handler,  otherwise it pass it through
    __m.job_instance = job_instance

    # Check to see if job is clear to run
    if not _can_run(job_def):
        job_instance.skip()
        return

    if platform.system() == 'Windows':
        args = ['cmd', '/C']  
        args = ['powershell', '-c']  
    else:
        args = ['bash', '-c']
    args.append(job_def['command'])
    th_out, th_err = None, None
    started_output = False
    parent_pid = os.getpid()
    if job_def:
        ''' SO code, simpler  '''
        '''
        with subprocess.Popen(args, stdout=PIPE, stderr=STDOUT, text=True) as process:
            process = process
            process_pid = process.pid
            job_instance.save_pid(process.pid)
            for line in process.stdout:
                if not started_output:
                    job_instance.go()
                    started_output = True
                append_log(job_instance.id, 'stdout', line)

            print(process)
            print('arj pid: %s' % process_pid)
            p_res = process.poll()
            print(p_res) 

        if process.returncode == 0:
            job_instance.complete()
        else:
            job_instance.error()
        print(f'waiting for {parent_pid} to clear zombie')
        wait_pid(parent_pid)
        #wait_pid(process_pid)
        clear_zombie(parent_pid)  # TODO might not need this
        '''


        ''' Your code, bit naff, might have contention between stdout and stderr threads? '''
        job_instance.go()
        process = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
        process = process
        process_pid = process.pid
        job_instance.save_pid(process_pid)
        th_out = Thread(target=_stream_pipe, args=['stdout', process, job_instance], daemon=True)
        th_out.start()
        th_err = Thread(target=_stream_pipe, args=['stderr', process, job_instance], daemon=True)
        th_err.start()
        timed_out = False
        while True:
            # while (so := process.stdout.readline()):
            #     print(so)
            # while (se := process.stderr.readline()):
            #     print(se)
            pres = process.poll()
            if pres is not None:
                print(pres)
                time.sleep(0.5)
                break

            if timeout_dt and (datetime.now() > timeout_dt):
                timed_out = True
                #process.kill()
                _kill_process_tree(process.pid)  # kills subprocesses e.g. those spawned using processpoolexecutor

            time.sleep(1)
          

        if timed_out:
            job_instance.timed_out()
            _run_following_jobs('error', job_instance.id, job_def)
        elif process.returncode == 0:
            job_instance.complete()
            _run_following_jobs('next', job_instance.id, job_def)
        else:
            job_instance.error()
            _run_following_jobs('error', job_instance.id, job_def)

        print(f'waiting for {parent_pid} to clear zombie')
        wait_pid(parent_pid)
        #wait_pid(process_pid)
        clear_zombie(parent_pid)  # TODO might not need this
        #clear_zombie(process_pid)
        
        if th_out:
            th_out.join()
        if th_err:
            th_err.join()

        zip_log(job_instance.id)


    




def run_job(jobname):
    """ Interface to the job running code.
    Spawns an instance of this code in job running mode """
    
    args = copy(sys.argv)
    
    args = [sys.executable]
    # module_name = sys.modules[__name__]

    # If run via python env and library e.g. python -m procmanager insteads of kin
    if 'py' in str(sys.executable).lower():
        module_name = 'procmanager'
        args += ['-m', module_name]

    # args.append('--jobname')
    args.append('run')
    args.append(jobname)  # i.e. kin run JOBNAME
    # args = [sys.executable] + args
    print(args)
    try:
        p = subprocess.Popen(args, cwd=config.RUN_DIR) #, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(e)

