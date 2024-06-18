# Main entry point
from procmanager.__main__ import main


'''
import argparse

from procmanager.job_instance import actually_run_job
from procmanager.server import start_server

def serve(args):
    start_server()

def run(args):
    if args.jobname:
        actually_run_job(args.jobname)
    else:
        args.sub_parser.print_help()

def show_help( args):
    args.parser.print_usage()

def main():
    """ quick primer on argparse:
          subparsers are subcommands in argparse. set_defaults sets the function to run.
         args.func(args) actually runs the command 
         """
    parser = argparse.ArgumentParser()
    # parser.add_argument("--jobname", type=str)
    
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    parser_serve = subparsers.add_parser('serve')
    parser_serve.set_defaults(func=serve)
    parser_run = subparsers.add_parser('run')
    parser_run.set_defaults(func=run, sub_parser=parser_run)
    parser_run.add_argument('jobname')
    parser_help = subparsers.add_parser('help')
    parser_help.set_defaults(func=show_help, parser=parser)
    #foo_parser = subparsers.add_parser('foo')
    #parser.add_argument("--serve")
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)  
    else:
        parser.print_help()

    # if args.jobname:
    #     actually_run_job(args.jobname)
    # else:
    #     start_server()
'''
if __name__ == "__main__":
    main()
