"""
Module with all the extensions used by the app.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_stats import Stats
from flask_cors import CORS

db = SQLAlchemy()
stats = Stats()
cors = CORS()
