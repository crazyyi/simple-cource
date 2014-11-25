from apps import app
import logging
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

def main():
    logging.basicConfig(format='localhost -- [%(asctime)s]%(message)s', level=logging.DEBUG)
    log = logging.getLogger(__name__)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    main()
    manager.run()
