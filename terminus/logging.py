import logging
import os
import sys

class LogPrint(object):
    '''
    This class is used in place of the standard python print for simultaneous printing and logging depending on the desired verbosity
    '''

    def __init__(self, log, vb):
        '''
        Requires a logging obj and verbosity level
        '''

        # Must be either a Logger object or None
        if log is not None:
            if not isinstance(log, logging.Logger):
                raise TypeError('log must be either a Logger ' +\
                                'instance or None!')

        self.log = log
        self.vb = vb

        return

    def __call__(self, msg=None):
        '''
        treat it like print()
        e.g. lprint = LogPrint(...); lprint('message')
        '''

        if msg is None:
            msg = ''

        if self.log is not None:
            self.log.info(msg)
        if self.vb is True:
            print(msg)

        return

    def debug(self, msg):
        '''
        don't print for a debug
        '''
        self.log.debug(msg)

        return

    def warning(self, msg):
        self.log.warning(msg)
        if self.vb is True:
            print(msg)

        return

class Logger(object):

    def __init__(self, logfile, logdir=None):
        if logdir is None:
            logdir = './'

        self.logfile = os.path.join(logdir, logfile)

        # only works for newer versions of python
        # log = logging.basicConfig(filename=logfile, level=logging.DEBUG)

        # instead:
        log = logging.getLogger()
        log.setLevel(logging.INFO)
        # log.setLevel(logging.ERROR)
        handler = logging.FileHandler(self.logfile, 'w', 'utf-8')
        handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
        log.addHandler(handler)

        self.log = log

        return

def setup_logger(logfile, logdir=None):
    '''
    Utility function if you just want the log and not the Logger object
    '''

    if logdir is not None:
        if not os.path.exists(logdir):
            os.makedirs(logdir)

    logger = Logger(logfile, logdir=logdir)

    return logger.log
