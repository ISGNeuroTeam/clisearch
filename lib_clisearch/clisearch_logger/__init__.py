
# from . import logger
import logging
import sys


def get_logger(out, loglevel, reinit=False):
    cfg = None
    logger = logging.getLogger(None)
    if reinit:
        for h in logger.handlers:
            logger.removeHandler(h)
    if len(logger.handlers)>0:
        return logger
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-s PID=%(process)d %(module)s:%(lineno)d func=%(funcName)s - %(message)s'
    )

    if out.upper() in ('STDERR', 'STDOUT'):
        if out.upper() == 'STDOUT':
            ch = logging.StreamHandler(stream=sys.stdout)
        else:
            ch = logging.StreamHandler(stream=sys.stderr)

        ch.setFormatter(formatter)
        ch.setLevel(loglevel.upper())
        logger.addHandler(ch)

    elif out.upper() == 'NULL':
        logger.addHandler(logging.NullHandler())

    else:
        fh = logging.FileHandler(out)
        fh.setFormatter(formatter)
        fh.setLevel(loglevel.upper())
        logger.addHandler(fh)

    logger.setLevel(loglevel.upper())
    return logger
