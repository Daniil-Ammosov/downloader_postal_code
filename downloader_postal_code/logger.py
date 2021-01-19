# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler


DICT_LOG_LVL = {
    "debug":    logging.DEBUG,
    "info":     logging.INFO,
    "warning":  logging.WARNING,
    "error":    logging.ERROR
}

LOG_FILE = "/var/log/downloader_postal_code/log"
LOGGER_NAME = 'downloader_postal_code'


def get_logger(name=LOGGER_NAME):
    message_format = u"%(asctime)s|%(name)s|%(levelname)5s| MESSAGE: %(message)s"
    datetime_format = u"[%d.%m.%Y %H:%M:%S]"
    formatter = logging.Formatter(fmt=message_format, datefmt=datetime_format)

    filehandler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=1024 * 1024 * 10,
        backupCount=10,
        encoding="utf-8"
    )
    filehandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(filehandler)

    return logger


def set_log_lvl(log_lvl, name=LOGGER_NAME):
    logging.getLogger(name).setLevel(DICT_LOG_LVL.get(log_lvl, logging.INFO))
