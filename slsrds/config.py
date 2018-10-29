import configparser
import os

CONFIG_DIR = 'config'


def get_config():
    stage = os.getenv('STAGE')
    config = configparser.ConfigParser()
    path = os.path.join(CONFIG_DIR, f'slsrds.{stage}.ini')
    if os.path.exists(path):
        config.read(path)
    else:
        path = os.path.join(CONFIG_DIR, 'slsrds.ini')
        if os.path.exists(path):
            config.read(path)
        else:
            raise Exception(
                f'No slsrds.ini or slsrds.{stage}.ini configuration file found')
    return config
