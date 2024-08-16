Process Runner:
===============

Runs processes on a schedule and monitors results.

Allows authenticated remote execution of pre-defined jobs.

Written to coordinate data processing tasks.

Usage:
======

`pip install procmanager`

Run web server TODO
`pm-cli`

Run particular job by name
`pm-cli --jobname <jobname>`


dev mode:
---------
This is mostly intended to run in user space.

build package:
--------------
install dev requirements
`python -m build` in package directory

SSL:
====
We recommend using a reverse_proxy such as nginx apache or Caddy to provide SSL functionality.

Alternatives:
=============

- Cron (obviously!)
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
