import logging

from systemd.journal import JournalHandler

from openheat.config import config

logger_name = 'openheat'  # FIXME

logging.basicConfig(level=getattr(logging, config.log_level),
                    format='%(asctime)s %(name)-12s %(threadName)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(logger_name)
log.addHandler(JournalHandler())
