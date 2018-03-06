"""
macros
~~~~~~~~~~~~~~~~~~~~~~

Python app for finding and tracking common T&S macros
"""
import os
from dromedary import load_configuration

from flask_maker import create_app
import logging.config

__version__ = '0.1.0'
__author__ = 'T&S'
__email__ = 'trustandsafety-all@squarespace.com'
__description__ = 'Macros application for t&s language snippets'


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)


config = load_configuration(
    PROJECT_DIR,
    base_config_file='config.yaml',
    local_config_file='config.local.yaml',
    use_env_overrides=True
)


def setup_logging(logging_config):
    if logging_config:
        logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level='WARNING')


setup_logging(config.get('LOGGING'))


app = create_app(__name__, config)


from macros import views
from .util import filters

