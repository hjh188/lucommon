#!/usr/bin/env python

"""
log instance provider


configure `logger.conf` to setup logger
"""

import os
import logging
import logging.config

from utils import mkdir

try:
    from django.conf import settings
except ImportError:
    settings = None

######################
#  Customed Handler  #
######################
class LuTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Customed TimedRotatingFileHandler
    """
    def __init__(self, filename, when='D', interval=1, backupCount=15,
                                 encoding=None, delay=False, utc=False):
        if os.path.dirname(filename):
            mkdir(os.path.dirname(filename))

        logging.handlers.TimedRotatingFileHandler.__init__(self, filename, when,
                                                        interval, backupCount,
                                                        encoding, delay, utc)

logging.LuTimedRotatingFileHandler = LuTimedRotatingFileHandler


########################
#  Customed Formatter  #
########################
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'  : YELLOW,
    'INFO'     : WHITE,
    'DEBUG'    : BLUE,
    'CRITICAL' : RED,
    'ERROR'    : RED,
    'RED'      : RED,
    'GREEN'    : GREEN,
    'YELLOW'   : YELLOW,
    'BLUE'     : BLUE,
    'MAGENTA'  : MAGENTA,
    'CYAN'     : CYAN,
    'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"

class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color     = COLOR_SEQ % (30 + COLORS[levelname])
        message   = logging.Formatter.format(self, record)
        message   = message.replace("$RESET", RESET_SEQ)\
                           .replace("$BOLD",  BOLD_SEQ)\
                           .replace("$COLOR", color)
        for k,v in COLORS.items():
            message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                             .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                             .replace("$BG-" + k, COLOR_SEQ % (v+40))
        return message + RESET_SEQ

logging.ColorFormatter = ColorFormatter

disable_existing_loggers = False if settings and settings.APP_DEBUG else True
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logger.conf'), disable_existing_loggers=disable_existing_loggers)

#############################
# interface exposed outside #
#############################
# Just need to import lu_logger from other module,
#-use in this way:
#>>>lu_logger.debug('debug msg')
#>>>lu_logger.warn('warn msg')
lu_logger = logging.getLogger('root')


