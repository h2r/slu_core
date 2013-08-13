import time

def timedelta_to_seconds(td):
    """
    Convert a timedelta to float number of seconds. 
    """
    return td.days * 86400 + td.seconds + td.microseconds * 1e-6


def timedelta_to_micros(td):
    return timedelta_to_seconds(td) * 1e6



def datetime_to_seconds_offset(dt):
    return time.mktime(dt.timetuple()) + dt.microsecond * 1e-6


def overlaps(r1, r2):
    """
    In the allen relation sense. You probalby want intersects.
    """
    s1, e1 = r1
    s2, e2 = r2
    return s1 <= s2 and s2 <= e1 and s2 <= e2
    
    

def intersects(r1, r2):
    return overlaps(r1, r2) or overlaps(r2, r1)
    
    

def anyIntersect(ranges, r2):
    for r in ranges:
        if intersects(r, r2):
            return True
    return False


def datetime_to_fname(dt):
    """
    formats a date/time into something suitable for a filename.
    """
    return dt.strftime("%Y-%m-%d-%H-%M-%S")

