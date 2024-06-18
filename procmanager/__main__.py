# Main entry point
import argparse
from datetime import datetime

from procmanager.job_instance import actually_run_job
from procmanager.server import start_server
from procmanager.config import load_job_defs, CONFIG_FILES
import procmanager.db

def serve(args):
    start_server(args=args) # must use named arguments

def run(args):
    if args.jobname:
        actually_run_job(args.jobname)
    else:
        args.sub_parser.print_help()

def show_help( args):
    args.parser.print_usage()

def list_(args):
    import toml
    #print(load_job_defs())
    print(toml.dumps(load_job_defs()))
    # TODO should really print the original files with comments here. maybe get people to put comments in a description/help/comments field


def show_log(args):
    properties = ['id', 'status', 'started_at', 'finished_at', 'pid', 'running_length'] #jobname
    for ji in procmanager.db.list_job_instances():
        ji = {k:v for k, v in ji.items() if k in properties}
        ji['started_at'] = datetime.fromtimestamp(ji['started_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['started_at'] else None
        ji['finished_at'] = datetime.fromtimestamp(ji['finished_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['finished_at'] else None
        print(ji)


def edit(args):
    # get editor
    # with NamedTemporaryFile
    # open example.toml
    # then save example.toml
    # then reload config in the scheduler
    # TODO
    print(load_job_defs())


def reload(args):
    # TODO
    host, port = 'localhost', 8737
    auth = None
    requests.get(f'{host}:{port}/reload_config')

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
    parser_serve.add_argument('--port', default=8737, type=int)
    parser_run = subparsers.add_parser('run')
    parser_run.set_defaults(func=run, sub_parser=parser_run)
    parser_run.add_argument('jobname')
    parser_help = subparsers.add_parser('help')
    parser_help.set_defaults(func=show_help, parser=parser)
    parser_list = subparsers.add_parser('list')
    parser_list.set_defaults(func=list_, sub_parser=parser_list)
    parser_edit = subparsers.add_parser('edit')
    parser_edit.set_defaults(func=edit, sub_parser=parser_edit)
    parser_log = subparsers.add_parser('log')
    parser_log.set_defaults(func=show_log, sub_parser=parser_log)
    parser_reload = subparsers.add_parser('reload')
    parser_reload.set_defaults(func=reload, sub_parser=parser_reload)
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

if __name__ == "__main__":
    main()
