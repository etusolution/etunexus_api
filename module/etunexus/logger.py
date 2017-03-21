# -*- coding: utf-8 -*-

import logging


def get_logger(level=logging.INFO):
    logger = logging.getLogger('etu.nexus')
    logger.setLevel(level)
    if not len(logger.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)d - %(message)s'))
        logger.addHandler(ch)

    return logger
