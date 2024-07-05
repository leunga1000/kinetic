import time
from threading import Timer
from croniter import croniter
from datetime import datetime
import dateparser
from procmanager.job_instance import run_job
from procmanager import db
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
log = logging.Logger('PythonProcessRunner')
#logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
#    datefmt="%m/%d/%y %I:%M:%S %p",)

class Job:
    def __init__(self, jobname, schedule, command, givewayto=None, comments=None, timeout=None, **args):
        self.schedule = schedule
        if not croniter.is_valid(schedule):
            log.error('Couldn''t parse cron schedule! "' + schedule + '" for ' + jobname + '. Not scheduling.')
            self.schedule = None

        self.jobname = jobname
        self.command = command
        self.givewayto = givewayto
        self.comments = comments
        self.timeout = timeout # see job_instance.py:get_timeout_dt for conversion, can validate it here with that function
        log.debug(f"Unused arguments {args} for {jobname}")
        self.running_jobs = []
        self.play()
        'THIS MAY BLOCK HERE'

    def get_next_time(self):
        if not self.schedule:
            return
        #base = datetime(2000, 1, 1, 0, 0)
        iter = croniter(self.schedule)
        # iter.get_current()
        return iter.get_next(datetime) 
    
    def _schedule_next(self):
        next_time = self.get_next_time()
        if not next_time:
            return
        wait_time = (next_time - datetime.now()).total_seconds()
        self.timer = Timer(wait_time, self.run_instance, args=None, kwargs=None)
        self.timer.daemon = True
        self.timer.start()

    def pause(self):
        self.timer.cancel() if self.timer else None

    def play(self):
        self._schedule_next()
 
    def _can_run(self):
        for priority_job_name in self.givewayto or []:
            if db.is_job_running(priority_job_name):
                return False 
        return True

    def run_instance(self):
        try:
            run_job(self.jobname)
        finally:
            time.sleep(1)  # croniter resolution seems to be one second
            #t = Thread(target=self._schedule_next, daemon=True)
            #t.start()
            self._schedule_next()


# necessary?
def create_job(jobname, schedule, command, givewayto):
    j = Job(jobname, schedule, command, givewayto)
    return j
