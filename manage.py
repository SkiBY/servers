# coding=utf-8 
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from c_base import app, db

#from models import *
migrate = Migrate(app, db)

# Инициализируем менеджер
manager = Manager(app)
# Регистрируем команду, реализованную в виде потомка класса Command
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()