import datetime

def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r

def get_current_timestamp():
    return datetime.datetime.now(tz =  datetime.datetime.now().astimezone().tzinfo).isoformat(timespec='milliseconds')

class Unsupported_by_ODS(Exception):
    pass

