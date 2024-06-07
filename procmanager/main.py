# Main entry point
import argparse

from procmanager.job_instance import actually_run_job
from procmanager.server import start_server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobname", type=str)
    args = parser.parse_args()

    # Two modes
    if args.jobname:
        actually_run_job(args.jobname)
    else:
        start_server()

if __name__ == "__main__":
    main()