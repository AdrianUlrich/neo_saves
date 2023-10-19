from configparser import SafeConfigParser

NEO_EXE_FOLDER_C = 'NEO.exe folder'


def make_config():
    config.add_section('main')
    config.set('main', NEO_EXE_FOLDER_C, '')

    with open('config.ini', 'x') as configfile:
        config.write(configfile)

    print('Config file created.')


config = SafeConfigParser()


def set_config(key, value):
    config.set('main', key, value)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
