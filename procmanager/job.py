from threading import Timer
from croniter import croniter
from datetime import datetime
from procmanager.job_instance import run_job
import logging

log = logging.Logger('PythonProcessRunner')

class Job:
    def __init__(self, jobname, schedule, command):
        self.schedule = schedule
        if not croniter.is_valid(schedule):
            log.error('Invalid cron schedule! ' + schedule + '. Not scheduling.')
            self.schedule = None

        self.jobname = jobname
        self.command = command
        self.play()

    def get_next_time(self):
        iter = croniter(self.schedule, base=None)
        # iter.get_current()
        return iter.get_next(datetime) 
    
    def schedule_next(self):
        wait_time = self.get_next_time() - datetime.now()
        self.timer = Timer(wait_time, self.run_instance, args=None, kwargs=None)
        self.timer.start()

    def pause(self):
        self.timer.cancel()

    def play(self):
        self.schedule_next()

    def run_instance(self):
        run_job(self.jobname)
        self.schedule_next()

    


def create_job(jobname, schedule, command):
    j = Job(jobname, schedule, command)
    return j
