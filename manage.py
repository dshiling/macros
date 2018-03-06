#!/usr/bin/env python
from flask_script import Server, Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from macros import app
from macros.extensions import db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('runserver', Server())
manager.add_command('shell', Shell())
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
