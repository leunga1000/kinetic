# Main entry point
import argparse

from job_instance import run_job
from server import start_server

if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobname", type=str)
    args = parser.parse_args()

    # Two modes
    if args.jobname:
        run_job(args.jobname)
    else:
        start_server()