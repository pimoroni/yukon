LOG_NONE = 0
LOG_WARN = 1
LOG_INFO = 2
LOG_DEBUG = 3

level = LOG_INFO


def warn(objects='', sep='', end='\n'):
    if level >= LOG_WARN:
        print(objects, sep=sep, end=end)


def info(objects='', sep='', end='\n'):
    if level >= LOG_INFO:
        print(objects, sep=sep, end=end)


def debug(objects='', sep='', end='\n'):
    if level >= LOG_DEBUG:
        print(objects, sep=sep, end=end)
