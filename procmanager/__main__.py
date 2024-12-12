# Main entry point
import argparse
from datetime import datetime
import gzip
import os
import glob

from procmanager.job_instance import actually_run_job
from procmanager.config import load_job_defs, LOG_DIR, BASE_PATH, HOME_BIN
from procmanager.install import install, upgrade
import procmanager.db

def serve(args):
    from procmanager.server import start_server
    start_server(args=args) # must use named arguments

def run(args):
    if args.jobname:
        actually_run_job(args.jobname)
    else:
        args.sub_parser.print_help()

def show_help( args):
    args.parser.print_help()

def list_(args):
    import toml
    #print(load_job_defs())
    print(toml.dumps(load_job_defs()))
    # TODO should really print the original files with comments here. maybe get people to put comments in a description/help/comments field


from colorama import just_fix_windows_console
just_fix_windows_console()
from termcolor import colored
# There's also blessings for bold, underline.

def show_log_app(args):
    from procmanager.prompt_view import run_app
    run_app()

def show_log(args):
    from procmanager.tui_helpers import generate_log_table
    import rich
    from rich import print as rprint, table, box


    if hasattr(args, 'follow') and args.follow:
        import rich.live, time
        def get_table():
            rows, properties = generate_log_table() 
            t = table.Table(box=box.MINIMAL_HEAVY_HEAD, expand=True)
            for p in properties:
                t.add_column(p)
            for row in rows[-25:]:
                #rprint(*row)
                t.add_row(*[str(r) for r in row])
            return t
        t = get_table()
        with rich.live.Live(t, refresh_per_second=0.25) as live_table:
            while True:
                live_table.update(t)
                time.sleep(4)
                t = get_table()
    else:
        rows, properties = generate_log_table() 
        import tabulate
        from termcolor import cprint
        #cprint(tabulate.tabulate(rows[-1000:]))
        print(tabulate.tabulate(rows[-1000:]))
        return
        #rprint(tabulate.tabulate(rows[-50:]))
        #from rich.console import Console
        #console = Console()
        console.print(tabulate.tabulate(rows[-1000:]), highlight=False)
        #for row in rows:
        #   rprint(tabulate.tabulate(row))
        #rich.print(t)

""" TODO remove, moved to tui_helpers.py 
def generate_log_table(args):
    properties = ['id', 'status', 'started_at', 'finished_at', 'pid', 'running_length'] #jobname
    # There's also blessings for bold, underline.
    def format_value(k, v):
        if k == 'status':
            if v == 'OK':
                #v = f'[green]{v}[/green]'
                v = colored(v, 'green') 
            elif v == 'NW':
                #v = f'[cyan]{v}[/cyan]'
                v = colored(v, 'cyan', attrs=["blink"]) 
            elif v == 'SK':
                #v = f'[bright_black]{v}[/bright_black]'
                v = colored(v, 'dark_grey')
            elif v == 'ER':
                #v = f'[red]{v}[/red    ]'
                v = colored(v, 'red')
            elif v == 'GO':
                #v = f'[red]{v}[/red    ]'
                v = colored(f'{v}', 'blue', 'on_black', attrs=["blink"])  # reverse
        return str(v)
    rows = []
    for ji in procmanager.db.list_job_instances():
        ji = {k:v for k, v in ji.items() if k in properties}
        ji['started_at'] = datetime.fromtimestamp(ji['started_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['started_at'] else None
        ji['finished_at'] = datetime.fromtimestamp(ji['finished_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['finished_at'] else None
        #print(*list(ji.values()))
        rows.append([format_value(k,v) for k,v in ji.items()])
    return rows, properties 
"""



def edit(args):
    # get editor
    # launch editor with solo file if only one file or allow user to choose a file.
    # or show all jobs and save the changes to the respective file.
    #from configparser import ConfigParser
    #cp = ConfigParser(allow_unnamed_section=True)
    # if linux
    
    config_files = glob.glob(f'{BASE_PATH}/job_defs/*')
    se_path = '~/.selected_editor'
    se_path = os.path.expanduser(se_path)
    if os.path.exists(se_path):
        with open(se_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('SELECTED_EDITOR='):
                editor = line.split('=')[1].strip()
                editor = editor[1:-1]  # '/usr/bin/nano'
                print(editor)
                print(config_files)
                os.system(f'echo {editor} {" ".join(config_files)}')
                os.system(f'{editor} {" ".join(config_files)}')


    # with NamedTemporaryFile
    # open example.toml
    # then save example.toml
    # then reload config in the scheduler
    # TODO
    print(load_job_defs())


#def reload(args):
#    # TODO
#    host, port = 'localhost', 8737
#    auth = None
#    requests.get(f'{host}:{port}/reload_config')

def print_job_log(args):
    job_log_path = f"{LOG_DIR}/{args.job_id}.log"
    open_fn = open
    open_mode = 'r'
    if not os.path.exists(job_log_path):
        job_log_path = job_log_path + '.gz'
        open_fn = gzip.open
        open_mode = 'rt'

    with open_fn(job_log_path, open_mode) as f:
        for line in f.readlines():
            print(line, end='')

    print(args.edit)

def start(args):
    """ create and start systemctl service or win service """
    install() 

def stop(args):
    """ stop systemctl service or win service """
    os.system("systemctl --user stop kin") 
    os.system("systemctl --user status kin") 

def upgrade(args):
    """ Upgrade and copy binary to $HOME/bin - ought to be interacive"""
    maybe_yes = input("Are you sure you wish to upgrade kin binary y/n")
    if maybe_yes == 'y':
        upgrade()

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
    parser_log = subparsers.add_parser('ll', help="log in live mode")
    parser_log.add_argument('follow', action='store_true', default=True)
    parser_log.set_defaults(func=show_log, sub_parser=parser_log)
    parser_log = subparsers.add_parser('lll', help="log in live mode")
    parser_log.add_argument('follow', action='store_true', default=True)
    parser_log.set_defaults(func=show_log_app, sub_parser=parser_log)
    parser_print_job_log = subparsers.add_parser('jl', help="show/edit (cat/$EDITOR) output for job_id", aliases=['cat'])
    parser_print_job_log.add_argument('job_id', type=str)
    parser_print_job_log.add_argument('--edit', '-e', action='store_true', default=False)
    parser_print_job_log.set_defaults(func=print_job_log, sub_parser=parser_print_job_log)
    parser_start = subparsers.add_parser('start')
    parser_start.set_defaults(func=start, sub_parser=parser_start)
    parser_stop = subparsers.add_parser('stop')
    parser_stop.set_defaults(func=stop, sub_parser=parser_stop)
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
