Kinetic, a process runner:
==========================

Runs processes on a schedule and monitors results.

Allows authenticated remote execution of pre-defined jobs.

Written to coordinate data processing tasks.

Usage:
======

- After downloading the binary from the releases page and store in your $HOME/bin directory

``pm-cli install``

to install a user service that will schedule jobs.

Configuration file:
===================
Any .toml file in ~/.pm_dir will be loaded. Example config:

::
[print-output]
schedule="0 13 * * *"
command="python -c 'print(\"hello\");raise Exception(\"2\")'"


Building:
=========
After cloning repo, installing dev and application requirements.txt
``install.sh`` will build the application and distribute it to your home/bin directory.

Run particular job by name
``pm-cli run <jobname>``


dev mode:
---------
This is mostly intended to run in user space.


error modes:
============

messaging:
==========
email

uptimerobot


Alternatives:
=============

- Cron (obviously!)
- anacron
- Cronitor - email and status service, keep using cron jobs.
- Python Scheduler, APScheduler
- systemd timers
- jobflow, jobflow remote
- AWS Lambda, Step Functions and EventBridge
    - immense fun and basically free for small tasks, watch out for storage and bandwidth
- Julia Oxygen, TaskSchedule.jl
- Ray - Remote actors
- Rufus Scheduler
- Crystal Tasker
- Rust scheduler
- airflow et. al
