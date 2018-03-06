import logging

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import url
from sqlalchemy.exc import OperationalError
from werkzeug.utils import cached_property


logger = logging.getLogger(__name__)


class PostgresDatabase(object):
    """
    Postgres DB target, uses SQLAlchemy to load tables and execute SQL code
    """

    def __init__(self, uri=None, **config):
        if config:
            config['drivername'] = 'postgresql'
            uri = url.URL(**config)
        self.uri = uri

    @cached_property
    def engine(self):
        return create_engine(self.uri)

    @cached_property
    def metadata(self):
        return MetaData(self.engine)

    def load_table(self, name, schema=None):
        return Table(name, self.metadata, autoload=True, schema=schema)

    def check_connection(self):
        try:
            connection = self.connect()
            connection.close()
            return True
        except OperationalError as error:
            logger.error('Operational error: {}'.format(error))
            return False

    def connect(self):
        return self.engine.connect()
