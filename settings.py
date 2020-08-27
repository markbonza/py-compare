from os import makedirs
from os.path import abspath, dirname, exists, join
import json, sys

if getattr(sys, 'frozen', False):
    BASE_PATH = dirname(sys.executable)
elif __file__:
    BASE_PATH = dirname(abspath(__file__))

LOCAL_PATH = '{}/local/'.format(BASE_PATH)
LOG_PATH = "{}logs/".format(LOCAL_PATH)

CONFIG_FILE = join(BASE_PATH, 'config.json')

if not exists(LOCAL_PATH):
    print('Creating directory...{}'.format(LOCAL_PATH))
    makedirs(LOCAL_PATH)

if not exists(LOG_PATH):
    print('Creating directory...{}'.format(LOG_PATH))
    makedirs(LOG_PATH)