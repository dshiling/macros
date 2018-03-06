"""
macros
~~~~~~~~~~~~~~~~~~~~~~

Python app for finding and tracking common T&S macros
"""
import os
from flask import Flask

__version__ = '0.1.0'
__author__ = 'dshiling'
__description__ = 'Macros application for common language snippets'

app = Flask(__name__)


from macros import views
from .util import filters

