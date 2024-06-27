import psutil


def is_running(pid):
    try:
        process = psutil.Process(pid)
        # process.status() can be running sleeping waking zombie, many. 
        #if process.status() not in (psutil.STATUS_DEAD, psutil.STATUS_ZOMBIE):
        if process.status() not in (psutil.STATUS_DEAD, ):
            return process
        else:
            return False
    except Exception as e:
        print(e)
        return False


def poll_pid(pid):
    if pid is None:
        return
    try:
        process = psutil.Process(pid)
    except Exception as e:
        print(e)
        return False
