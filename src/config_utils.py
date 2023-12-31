import logging
from configparser import SafeConfigParser

SAVEFILE_PATH_C = 'NEO.exe folder'
GAMEFILE_PATH_C = 'GAMEFILE_PATH'

config = SafeConfigParser()


def initialize():
    config.add_section('main')
    config.set('main', SAVEFILE_PATH_C, '')
    config.set('main', 'Logging Level', str(logging.WARNING))

    with open('config.ini', 'x') as configfile:
        config.write(configfile)

    logging.info('Config file created.')


def set_c(key, value):
    config.set('main', key, value)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
