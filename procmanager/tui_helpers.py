import procmanager.db
from datetime import datetime
from termcolor import colored

def generate_log_table(top_down=False, ptk=False, limit=None, offset=None):
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
            elif v == 'EX':
                #v = f'[red]{v}[/red    ]'
                v = colored(f'{v}', 'white', 'on_black', attrs=["blink"])  # reverse
            elif v == 'TI':
                #v = f'[red]{v}[/red    ]'
                v = colored(f'{v}', 'yellow', 'on_black', attrs=["blink"])  # reverse
            elif v == 'CL':
                #v = f'[red]{v}[/red    ]'
                v = colored(f'{v}', 'magenta', 'on_black', attrs=["blink"])  # reverse
        return v
    def format_value_ptk(k, v):
        v = str(v) 
        if k == 'status':
            if v == 'OK':
                #v = f'[green]{v}[/green]'
                v = ('fg:green', v + "\t")
            elif v == 'NW':
                #v = f'[cyan]{v}[/cyan]'
                #v = colored(v, 'cyan', attrs=["blink"])
                v = ('fg:cyan blink', v)
            elif v == 'SK':
                #v = f'[bright_black]{v}[/bright_black]'
                #v = colored(v, 'dark_grey')
                v = ('fg:darkgrey', v)
            elif v == 'ER':
                #v = f'[red]{v}[/red    ]'
                #v = colored(v, 'red')
                v = ('fg:red', v)
            elif v == 'GO':
                #v = f'[red]{v}[/red    ]'
                #v = colored(f'{v}', 'white', 'on_black', attrs=["blink"])  # reverse
                v = ('fg:blue bg:black blink', v)
            elif v == 'EX':
                v = ('fg:white bg:black blink', v)
            elif v == 'TI':
                v = ('fg:yellow bg:black blink', v)
            elif v == 'CL':
                v = ('fg:magenta bg:black blink', v)
        else:
            v = ('', v)
        return v
    rows = []
    for ji in procmanager.db.list_job_instances(top_down=top_down, limit=limit, offset=offset):
        ji = {k:v for k, v in ji.items() if k in properties}
        ji['started_at'] = datetime.fromtimestamp(ji['started_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['started_at'] else None
        ji['finished_at'] = datetime.fromtimestamp(ji['finished_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['finished_at'] else None
        #print(*list(ji.values()))
        if ptk:
            rows.extend([format_value_ptk(k,v) for k,v in ji.items()])
            rows.append(('', '\n'))
        else:
            rows.append([format_value(k,v) for k,v in ji.items()])
    return rows, properties


if __name__ == '__main__':
    rows, properties = generate_log_table()
