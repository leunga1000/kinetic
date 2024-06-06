from job import Job
from config import load_config
from dynamic_user_config import add_to_dynamic_config, remove_from_dynamic_config
import logging
log = logging.Logger('PythonProcessRunner')


class Scheduler:
    def __init__(self):
        self.job_defs = {}
        self.jobs = {}
        self.reload()
    
    def make_job(self, jobname, schedule, command):
        self.job_defs[jobname] = {'jobname': jobname,
                                  'schedule': schedule,
                                  'command': command}
        if jobname in self.jobs:
            existing_job =  self.jobs[jobname]
            existing_job.pause()
            del self.jobs

        job = Job(jobname, schedule, command)
        self.jobs[jobname] = job
    
    def add_new_job(self, jobname, schedule, command):
        add_to_dynamic_config(jobname, schedule, command)
        self.make_job(jobname, schedule, command)

    def delete_job_forever(self, jobname):
        # This won't delete from user defined files!
        job = self.jobs.get(jobname)
        if job:
            job.pause()
            del job
        remove_from_dynamic_config(jobname)
        log.info(f'{jobname} removed, but won''t be removed from user config files')


    def reload(self):
        # reloads the jobs list and regenerates jobs
        for jobname, job in self.jobs.items():
            job.pause()
            del job
        self.jobs = {}

        self.job_defs = load_config()
        for jobname, job_def in self.job_defs.items():
            job =  Job(**job_def)
            self.jobs[jobname] = job
        