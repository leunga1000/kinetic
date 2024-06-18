import time
from threading import Timer
from croniter import croniter
from datetime import datetime
from procmanager.job_instance import run_job
from procmanager import db
import logging

log = logging.Logger('PythonProcessRunner')

class Job:
    def __init__(self, jobname, schedule, command, givewayto=None, comments=None, **args):
        self.schedule = schedule
        if not croniter.is_valid(schedule):
            log.error('Invalid cron schedule! ' + schedule + ' for ' + jobname + '. Not scheduling.')
            self.schedule = None

        self.jobname = jobname
        self.command = command
        self.givewayto = givewayto
        self.comments = comments
        log.warning(f"Unused arguments {args} for {jobname}")
        self.play()

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
        wait_time = (next_time - datetime.now()).seconds
        self.timer = Timer(wait_time, self.run_instance, args=None, kwargs=None)
        self.timer.start()

    def pause(self):
        self.timer.cancel()

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
            self._schedule_next()


# necessary?
def create_job(jobname, schedule, command, givewayto):
    j = Job(jobname, schedule, command, givewayto)
    return j
