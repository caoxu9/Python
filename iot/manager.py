import pymysql

pymysql.install_as_MySQLdb()
from app import create_app, db
from app.models import User, Permission,Role
from flask_script import Shell, Manager

app = create_app('develop')
from flask_migrate import Migrate, MigrateCommand

app.add_template_global(Permission, 'Permission')
manager = Manager(app)
migrate = Migrate(app, db)


def make_context():
    return dict(app=app,User=User,Role=Role)


manager.add_command('shell', Shell(make_context=make_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    t = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(t)


manager.run()
