import re
import logging


logger = logging.getLogger(__name__)


def label_columns(mapping):
    """Given a dict with names and SQLAlchemy columns, it will label the columns with that name"""
    columns = []
    for name, column in mapping.items():
        columns.append(column.label(name))
    return columns


def log_clause(clause):
    """ Logs SQL alchemy clause for debugging purposes """
    t = str(clause)
    params = clause.compile().params

    def token(m):
        return repr(params[m.group(1)])

    logger.debug(re.compile(r':(\w+)').sub(token, t))
