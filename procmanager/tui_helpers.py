import procmanager.db
from datetime import datetime, timedelta
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
            elif v == 'ER' or v.startswith('ER: '):
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

        if k == 'id' and  v.startswith('ER: '):
                #v = f'[red]{v}[/red    ]'
                v = colored(v, 'red')
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

    def format_time(dt, now, arrow=False, prev_date=None):
        if not dt:
            return None
        td = dt - now
        if dt.year > now.year:
            year_fmt = ',%y'
        else:
            year_fmt = ''
        sec_fmt = ''

        if dt.strftime('%Y%m%d') == now.strftime('%Y%m%d'):
            mth_day_fmt = ''
            sec_fmt = ':%S'
            sec_fmt = ''
        elif prev_date and dt.day == prev_date.day:
            mth_day_fmt = ''
        else:
            mth_day_fmt = '%b %d'
        arrow_fmt = ' ->- ' if arrow else '' 
        return dt.strftime(f'{mth_day_fmt} {year_fmt} %H:%M{sec_fmt} {arrow_fmt}')

    def format_seconds(seconds):
        seconds = round(seconds)
        days = minutes = hours = rem_seconds = ''
        if -10 < seconds < 60:
            rem_seconds = f'{seconds}s'
        elif 60 <= seconds < 3600:
            minutes = f'{int(seconds / 60)}m '
            rem_seconds = f'{int(seconds % 60)}s'
        elif 3600 <= seconds < 3600 * 24:
            hours = f'{int(seconds / 3600)}h '
            minutes = f'{int(seconds / 60)}m '
        elif seconds > 3600 * 24:
            days = f'{int(seconds / (3600 * 24) )}d '  # (86400)
            hours = f'{int(seconds / 3600)}h '
            minutes = f'{int(seconds / 60)}m '
        return f'{days}{hours}{minutes}{rem_seconds}'

        

    now = datetime.now()
    for ji in procmanager.db.list_job_instances(top_down=top_down, limit=limit, offset=offset):
        if ji.get('had_errors'):
            ji['id'] = "ER: " + ji['id']
        ji = {k:v for k, v in ji.items() if k in properties}
        started_at_dt = datetime.fromtimestamp(ji['started_at']) if ji['started_at'] else None
        finished_at_dt = datetime.fromtimestamp(ji['finished_at']) if ji['finished_at'] else None
        ji['started_at'] = format_time(started_at_dt, now, arrow=True) 
        ji['finished_at'] = format_time(finished_at_dt, now, arrow=False, prev_date = started_at_dt) 
        # ji['started_at'] = datetime.fromtimestamp(ji['started_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['started_at'] else None
        # ji['finished_at'] = datetime.fromtimestamp(ji['finished_at']).strftime('%Y-%m-%d %H:%M:%S') if ji['finished_at'] else None
        #print(*list(ji.values()))
        ji['running_length'] = f'{format_seconds(ji["running_length"])}'
        if ptk:
            rows.extend([format_value_ptk(k,v) for k,v in ji.items()])
            rows.append(('', '\n'))
        else:
            rows.append([format_value(k,v) for k,v in ji.items()])
    return rows, properties


if __name__ == '__main__':
    rows, properties = generate_log_table()
